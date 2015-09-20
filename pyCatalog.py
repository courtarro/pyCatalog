#!/usr/bin/env python

import jsonrpc
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sys
import threading
import time
import tornado.ioloop
import tornado.web

# --- Local imports ---

from amazon import Amazon
from config import *
from model import *
from utils import *

# --- Constants ---

LISTEN_PORT = 8000

# --- Globals ---

dispatcher = jsonrpc.Dispatcher()
amazon = Amazon()


# --- Methods ---

def write_new_item(new_item):
    engine = sa.create_engine('sqlite:///' + CATALOG_DB)
    Base.metadata.bind = engine
    session_spec = orm.sessionmaker()
    session_spec.bind = engine
    sess = session_spec()

    sess.add(new_item)
    sess.commit()
    new_id = new_item.id

    sess.close()

    return new_id


def test_amazon_query():
    amazon = Amazon()

    upc = '851147006055'
    items_a = amazon.search(upc)
    if (items_a is None) or (not len(items_a)):
        sys.exit("No item with that UPC")
    item_a = items_a[0]
    asin, item = amazon.to_item(item_a, upc)
    covers_a = amazon.get_item_imagesets(asin)
    if (covers_a is not None) and len(covers_a):
        for img_type, cover_a in covers_a.iteritems():
            url = amazon.get_best_image_url(cover_a)
            filename = fetch_image(url)
            if filename:
                img = Image(type=img_type, filename=filename)
                item.images.append(img)

    write_new_item(item)


def rpc_execute(request):
    response = jsonrpc.JSONRPCResponseManager.handle(request, dispatcher)
    return response.json


# --- JSON RPC methods ---

@dispatcher.add_method
def amazon_search(keywords):
    results = amazon.search(keywords)
    return results or False         # can't return None


@dispatcher.add_method
def amazon_get_image(asin):
    return amazon.get_item_image_url(asin) or False         # can't return None


@dispatcher.add_method
def amazon_add_item(**kwargs):
    asin = kwargs['asin']
    upc = kwargs['upc'] if kwargs.has_key('upc') else None

    # Look up the XML item entry (cached or new)
    item_x = amazon.lookup_with_cache(asin)
    if item_x is None:
        return False

    # Create a model Item object, if possible
    asin, new_item = amazon.to_item(item_x, upc)
    amazon.add_images_to_item(new_item, asin)
    new_id = write_new_item(new_item)

    return new_id


# --- Web server stuff ---

class FancyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_default_headers(self):
        # Allow other domains, prevent any caching
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


class RPCHandler(tornado.web.RequestHandler):
    def post(self):
        self.set_header('Content-Type', 'application/json')
        self.write(rpc_execute(self.request.body))


class WebServer():
    def __init__(self, port_number, www_root):
        self.port_number = port_number
        self.www_root = www_root

        # --- Tornado Server Startup ---
        self.application = tornado.web.Application([
            (r"/rpc", RPCHandler),                                                                           # json-rpc
            (r"/(.*)", FancyStaticFileHandler, {"path": self.www_root, "default_filename": "index.html"}),   # static
        ])

    def stop(self):
        tornado.ioloop.IOLoop.instance().add_callback(self._shutdown)

    def run(self):
        self.application.listen(self.port_number)
        print "HTTP server listening on port " + str(self.port_number)
        tornado.ioloop.IOLoop.instance().start()        # blocks here

    def _shutdown(self):
        tornado.ioloop.IOLoop.instance().stop()


# --- Main method ---

if __name__ == '__main__':
    server = WebServer(LISTEN_PORT, "www")

    t = threading.Thread(target=server.run)
    t.start()
    time.sleep(1)

    while True:
        try:
            raw_input("Press Enter to quit.\n")
            break
        except KeyboardInterrupt:
            pass

    server.stop()
    print "Shutting down..."
    t.join()
    print "Shutdown"
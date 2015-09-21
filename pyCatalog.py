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

def get_db_session():
    engine = sa.create_engine('sqlite:///' + CATALOG_DB)
    Base.metadata.bind = engine
    session_spec = orm.sessionmaker()
    session_spec.bind = engine
    sess = session_spec()

    return sess


def rpc_execute(request):
    response = jsonrpc.JSONRPCResponseManager.handle(request, dispatcher)
    return response.json


# --- JSON RPC methods ---

@dispatcher.add_method
def amazon_search(keywords):
    results = amazon.search(keywords)
    return results or False         # can't return None


@dispatcher.add_method
def amazon_lookup(**kwargs):
    if kwargs.has_key('asin'):
        item_id = kwargs['asin']
        id_type = 'ASIN'
    elif kwargs.has_key('upc'):
        item_id = kwargs['upc']
        if len(item_id) == 12: item_id = '0' + item_id
        id_type = 'EAN'
    elif kwargs.has_key('ean'):
        item_id = kwargs['ean']
        id_type = 'EAN'
    elif kwargs.has_key('isbn'):
        item_id = kwargs['isbn']
        id_type = 'ISBN'
    else:
        return False

    results = amazon.lookup(item_id, id_type)
    return results or False         # can't return None


@dispatcher.add_method
def amazon_get_image(asin):
    return amazon.get_item_image_url(asin) or False         # can't return None


@dispatcher.add_method
def amazon_add_item(**kwargs):
    asin = kwargs['asin']

    # Look up the XML item entry (cached or new)
    item_x = amazon.lookup_with_cache(asin, return_xml=True)
    if item_x is None:
        return False

    # Create a model Item object, if possible
    asin, new_item = amazon.to_item(item_x)

    # Add available external IDs
    if kwargs.has_key('upc'):
        new_item.external_ids.append(ExternalId(provider=ExternalIdProvider.UPC, external_id=kwargs['upc']))
    if kwargs.has_key('ean'):
        new_item.external_ids.append(ExternalId(provider=ExternalIdProvider.EAN, external_id=kwargs['ean']))
    if kwargs.has_key('isbn'):
        new_item.external_ids.append(ExternalId(provider=ExternalIdProvider.ISBN, external_id=kwargs['isbn']))

    # Begin DB access
    sess = get_db_session()

    # Check whether this item exists already
    num = sess.query(Item).join(Item.external_ids) \
        .filter(ExternalId.provider == ExternalIdProvider.Amazon) \
        .filter(ExternalId.external_id == asin).count()
    if num > 0:
        sess.close()
        return "Item already exists."

    # At this point, we know the item doesn't exist. Get the images of the product.
    amazon.add_images_to_item(new_item, asin)

    sess.add(new_item)
    sess.commit()
    sess.close()

    return False


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

#!/usr/bin/env python

import sys
from xmlrpclib import ServerProxy, Error

__author__ = 'Ethan Trewhitt'

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: upc_db.py <upc>'
        exit
    else:
        s = ServerProxy('http://www.upcdatabase.com/xmlrpc')
        params = {'rpc_key': UPC_DB_KEY, 'upc': sys.argv[1]}
        print s.lookup(params)



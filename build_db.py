#!/usr/bin/env python

import sqlalchemy as sa
import os
import sys

from config import *
from model import *

__author__ = 'Ethan Trewhitt'


if __name__ == '__main__':
    print "Do you really want to wipe out the whole DB?"
    sys.exit(1)

    try:
        os.remove(CATALOG_DB)
    except:
        pass
    engine = sa.create_engine('sqlite:///' + CATALOG_DB)
    Base.metadata.create_all(engine)

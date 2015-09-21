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


engine = sa.create_engine('sqlite:///' + CATALOG_DB)
Base.metadata.bind = engine
session_spec = orm.sessionmaker()
session_spec.bind = engine
sess = session_spec()

x = sess.query(Item).join(Item.external_ids).filter(ExternalId.provider == ExternalIdProvider.Amazon).filter(ExternalId.external_id == 'B00WWUD62U').count();
print x


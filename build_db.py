
import sqlalchemy as sa
import os

from config import *
from model import *

__author__ = 'Ethan Trewhitt'


if __name__ == '__main__':
    try:
        os.remove(CATALOG_DB)
    except:
        pass
    engine = sa.create_engine('sqlite:///' + CATALOG_DB)
    Base.metadata.create_all(engine)
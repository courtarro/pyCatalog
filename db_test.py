
import sqlalchemy as sa
import sqlalchemy.orm as orm
import sys

from config import *
from model import *

if __name__ == '__main__':
    engine = sa.create_engine('sqlite:///' + CATALOG_DB, echo=True)
    Base.metadata.bind = engine

    DBSession = orm.sessionmaker()
    DBSession.bind = engine

    sess = DBSession()

    print "Part 1"

    poly = orm.with_polymorphic(Item, [Movie, Music])
    all_items = sess.query(poly).filter(Movie.actor == "Brad Pitt").all()

    for item in all_items:
        if type(item) is Movie:
            print "Movie: " + str(item.title)
        elif type(item) is Music:
            print "Music: " + str(item.title)
        else:
            print "Unknown media type"

    #sys.exit(0)

    print "Part 2"

    new_movie = Movie()
    new_extid = ExternalId(provider=ExternalIdProvider.Amazon, external_id='ASDF')
    #sess.add(new_extid)
    new_movie.external_ids.append(new_extid)

    #new_movie = Movie()
    new_movie.title = 'Hello Bollywood!'
    new_movie.actor = 'Brad Pitt'
    new_movie.publisher = 'Mooooovies'
    sess.add(new_movie)
    sess.commit()

    print new_movie.id

    #new_movie.id = 50
    #sess.commit()

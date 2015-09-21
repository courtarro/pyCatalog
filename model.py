
import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


# Enumerations
class MediaType:
    Item, Movie, Music = range(3)

class ExternalIdProvider:
    NULL, UPC, EAN, ISBN, Amazon, IMDB, CDDB = range(7)

class ImageType:
    NULL, FrontCover, BackCover = range(3)


class ExternalId(Base):
    __tablename__ = 'external_id'

    item_id = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    provider = Column(Integer, primary_key=True)
    external_id = Column(Text)

    item = relationship('Item', backref='external_ids')


class Image(Base):
    __tablename__ = 'image'

    item_id = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    type = Column(Integer, primary_key=True)
    filename = Column(Text)

    item = relationship('Item', backref='images')


class Item(Base):
    __tablename__ = 'item'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True)
    type = Column(Integer)
    added = Column(DateTime, server_default=sa.text('CURRENT_TIMESTAMP'))
    modified = Column(DateTime, server_default=sa.text('CURRENT_TIMESTAMP'), onupdate=sa.func.utc_timestamp())

    __mapper_args__ = {
        'polymorphic_identity': MediaType.Item,
        'polymorphic_on': type
    }


class Music(Item):
    __tablename__ = 'music'

    item_id = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    title = Column(Text)
    artist = Column(Text)
    label = Column(Text)

    __mapper_args__ = {
        'polymorphic_identity': MediaType.Music,
    }


class Movie(Item):
    __tablename__ = 'movie'

    item_id = Column(ForeignKey('item.id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    title = Column(Text)
    actor = Column(Text)
    director = Column(Text)
    publisher = Column(Text)

    __mapper_args__ = {
        'polymorphic_identity': MediaType.Movie,
    }

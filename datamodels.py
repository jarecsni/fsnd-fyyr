
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from pytz import timezone
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Table, create_engine, DateTime, String, MetaData
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, scoped_session

db = SQLAlchemy()
Base = declarative_base()
engine = create_engine(
    "postgresql://johnnyjarecsni:korte321@localhost/sandbox",
    connect_args = {
        "port": 5432
    },
    echo="debug",
    echo_pool=True
)

db_session = scoped_session(
    sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
)

class Genre(Base):
    __tablename__ = 'genre'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class Show(Base):
    __tablename__ = 'show'
    venue_id = Column(ForeignKey("venue.id"), primary_key=True)
    artist_id = Column(ForeignKey("artist.id"), primary_key=True)
    start_time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    artist = relationship("Artist", back_populates="shows")
    venue = relationship("Venue", back_populates="shows")

    def __repr__(self):
        return f'<Show with Artist: {self.artist.name} at Venue: {self.venue.name} at: {self.start_time}>'

class VenueGenre(Base):
    __tablename__ = 'venue_genre'
    venue_id = Column(Integer, ForeignKey("venue.id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genre.id"), primary_key=True)
    
    def __repr__(self):
        return f'<VenueGenre for venue: {self.venue_id}, name: {self.name}>'

class Venue(Base):
    __tablename__ = 'venue'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    address = Column(String(120))
    phone = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    website_link = Column(String(500))
    seeking_talent = Column(Boolean)
    seeking_description = Column(String)
    shows = relationship("Show", back_populates="venue")
    genres = relationship(Genre, secondary="venue_genre")


    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'


class ArtistGenre(Base):
    __tablename__ = 'artist_genre'
    artist_id = Column(Integer, ForeignKey("artist.id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genre.id"), primary_key=True)
    def __repr__(self):
        return f'<Genre for artist: {self.artist_id}, name: {self.name}>'

class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    phone = Column(String(120))
    genres = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    website_link = Column(String(500))
    seeking_venue = Column(Boolean)
    seeking_description = Column(String)
    shows = relationship("Show", back_populates="artist")
    genres = relationship(Genre, secondary="artist_genre")

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'

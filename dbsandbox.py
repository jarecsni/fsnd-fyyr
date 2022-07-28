from flask import Flask
from sqlalchemy import Column, ForeignKey, Integer, Table, create_engine, DateTime, String
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import declarative_base, relationship, scoped_session, sessionmaker

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


Base = declarative_base()


## Relationships:
class Show(Base):
    __tablename__ = 'show'
    venue_id = Column(ForeignKey("venue.id"), primary_key=True)
    artist_id = Column(ForeignKey("artist.id"), primary_key=True)
    date_and_time = Column(DateTime, nullable=False)
    artist = relationship("Artist", back_populates="artistShows")
    venue = relationship("Venue", back_populates="venueShows")

class Venue(Base):
    __tablename__ = 'venue'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    address = Column(String(120))
    phone = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    venueShows = relationship("Show", back_populates="venue")

class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    city = Column(String(120))
    state = Column(String(120))
    phone = Column(String(120))
    genres = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    artistShows = relationship("Show", back_populates="artist")

# Base.metadata.create_all(bind=engine)

# db_session.add(
#     User(username="testuser", password_hash=b"", password_salt=b"", balance=1)
# )
# db_session.commit()

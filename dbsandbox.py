from flask import Flask
from pytz import timezone
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Table, create_engine, DateTime, String
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
    date_and_time = Column(DateTime(timezone=True), nullable=False, primary_key=True)
    artist = relationship("Artist", back_populates="shows")
    venue = relationship("Venue", back_populates="shows")

    def __repr__(self):
        return f'<Show with Artist: {self.artist.name} at Venue: {self.venue.name} at: {self.date_and_time}>'

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
    # additional fields (to be done in a migration)
    website_link = Column(String(500))
    seeking_talent = Column(Boolean)
    seeking_description = Column(String)
    # } migration end
    
    # migration: relations {
    shows = relationship("Show", back_populates="venue")
    genres = relationship("VenueGenre")
    # } migration end

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'

# migration { relations }
class VenueGenre(Base):
    __tablename__ = 'venue_genre'
    venue_id = Column(Integer, ForeignKey("venue.id"), primary_key=True)
    name = Column(String, nullable=False, primary_key=True)
    
    def __repr__(self):
        return f'<VenueGenre for venue: {self.venue_id}, name: {self.name}>'
# migration end

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
    # additional fields (to be done in a migration)
    website_link = Column(String(500))
    looking_for_venue = Column(Boolean)
    looking_for_description = Column(String)
    # } migration end
    shows = relationship("Show", back_populates="artist")
    genres = relationship("ArtistGenre")

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'

# migration relations
class ArtistGenre(Base):
    __tablename__ = 'artist_genre'
    artist_id = Column(Integer, ForeignKey("artist.id"), primary_key=True)
    name = Column(String, nullable=False, primary_key=True)
# } end migration 
    def __repr__(self):
        return f'<Genre for artist: {self.artist_id}, name: {self.name}>'
# Commands:

def createScheme():
    Base.metadata.create_all(bind=engine)

def loadVenue(name, city, state, address, phone, image_link, facebook_link, website_link, 
    seeking_talent, seeking_description, genres):
    venue = Venue(name, city, state, 
        address, phone, 
        image_link,
        facebook_link, website_link,
        seeking_talent, 
        seeking_description
    )
    db_session.add(venue)
    db_session.commit()

    for g in genres:
        db_session.add(VenueGenre(venue_id=venue.id, name=g))


def loadVenues():

    # The musical hop
    loadVenue(name='The musical hop', city='San Francisco', state='CA', 
        address='1015 Folsom Street', phone='123-123-1234', 
        image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
        facebook_link='https://www.facebook.com/TheMusicalHop', website_link='https://www.themusicalhop.com',
        seeking_talent=True, 
        seeking_description='We are on the lookout for a local artist to play every two weeks. Please call us.',
        genres=['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk']
    )

    # The dueling pianos bar
    loadVenue(name='The dueling pianos bar', city='New York', state='NY', 
        address="335 Delancey Street", phone="914-003-1132", 
        image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        facebook_link="https://www.facebook.com/theduelingpianos", 
        website_link="https://www.theduelingpianos.com",
        seeking_talent=False, 
        seeking_description='',
        genres=['Classical', 'R&B', 'Hip-Hop']
    )



    # example to access the genres relation
    # db_session.query(Venue).first().genres



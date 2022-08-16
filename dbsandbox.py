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

# migration { relations }
class VenueGenre(Base):
    __tablename__ = 'venue_genre'
    venue_id = Column(Integer, ForeignKey("venue.id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genre.id"), primary_key=True)
    
    def __repr__(self):
        return f'<VenueGenre for venue: {self.venue_id}, name: {self.name}>'
# migration end

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
    # additional fields (to be done in a migration)
    website_link = Column(String(500))
    seeking_talent = Column(Boolean)
    seeking_description = Column(String)
    # } migration end
    
    # migration: relations {
    shows = relationship("Show", back_populates="venue")
    genres = relationship(Genre, secondary="venue_genre")
    # } migration end

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'


# migration relations
class ArtistGenre(Base):
    __tablename__ = 'artist_genre'
    artist_id = Column(Integer, ForeignKey("artist.id"), primary_key=True)
    genre_id = Column(Integer, ForeignKey("genre.id"), primary_key=True)
# } end migration 
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
    # additional fields (to be done in a migration)
    website_link = Column(String(500))
    seeking_venue = Column(Boolean)
    seeking_description = Column(String)
    # } migration end
    shows = relationship("Show", back_populates="artist")
    genres = relationship(Genre, secondary="artist_genre")

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'


# Commands:

def createScheme():
    Base.metadata.create_all(bind=engine)

def loadVenue(id, name, city, state, address, phone, image_link, facebook_link, website_link, 
    seeking_talent, seeking_description, genres):
    venue = Venue(id=id, name=name, city=city, state=state, 
        address=address, phone=phone, 
        image_link=image_link,
        facebook_link=facebook_link, website_link=website_link,
        seeking_talent=seeking_talent, 
        seeking_description=seeking_description
    )
    db_session.add(venue)
    db_session.commit()

    
    for genre in genres:
        _genre = db_session.query(Genre).filter_by(name=genre).one_or_none() 
        if _genre:
            venue.genres.append(_genre)
        else:
            _genre = Genre(name=genre)
            db_session.add(_genre)
            venue.genres.append(_genre) 

    db_session.commit()

def loadVenues():
    # The musical hop
    loadVenue(id=1, name='The musical hop', city='San Francisco', state='CA', 
        address='1015 Folsom Street', phone='123-123-1234', 
        image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
        facebook_link='https://www.facebook.com/TheMusicalHop', website_link='https://www.themusicalhop.com',
        seeking_talent=True, 
        seeking_description='We are on the lookout for a local artist to play every two weeks. Please call us.',
        genres=['Jazz', 'Reggae', 'Swing', 'Classical', 'Folk']
    )

    # The dueling pianos bar
    loadVenue(id=2, name='The dueling pianos bar', city='New York', state='NY', 
        address="335 Delancey Street", phone="914-003-1132", 
        image_link="https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        facebook_link="https://www.facebook.com/theduelingpianos", 
        website_link="https://www.theduelingpianos.com",
        seeking_talent=False, 
        seeking_description='',
        genres=['Classical', 'R&B', 'Hip-Hop']
    )

    # Park Square Live Music & Coffee
    loadVenue(id=3, name="Park Square Live Music & Coffee", city="San Francisco", state='CA', 
        address="34 Whiskey Moore Ave", phone="415-000-1234", 
        image_link="https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        facebook_link="https://www.facebook.com/ParkSquareLiveMusicAndCoffee", 
        website_link="https://www.parksquarelivemusicandcoffee.com",
        seeking_talent=False, 
        seeking_description='',
        genres=["Rock n Roll", "Jazz", "Classical", "Folk"]
    )
    # example to access the genres relation
    # db_session.query(Venue).first().genres

def loadArtist(id, name, city, state, phone, image_link, facebook_link, website_link, 
    seeking_venue, seeking_description, genres):
    artist = Artist(
        id=id,
        name=name, city=city, state=state, 
        phone=phone, 
        image_link=image_link,
        facebook_link=facebook_link, 
        website_link=website_link,
        seeking_venue=seeking_venue, 
        seeking_description=seeking_description
    )
    db_session.add(artist)
    db_session.commit()

    for genre in genres:
        _genre = db_session.query(Genre).filter_by(name=genre).one_or_none() 
        if _genre:
            artist.genres.append(_genre)
        else:
            _genre = Genre(name=genre)
            db_session.add(_genre)
            artist.genres.append(_genre)

    db_session.commit()

def loadArtists():
    loadArtist(id=4, name='Guns N Petals', city='San Francisco', state='CA',
        phone='326-123-5000', 
        image_link='https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80', 
        facebook_link='https://www.facebook.com/GunsNPetals', 
        website_link='https://www.gunsnpetalsband.com',
        seeking_venue=True,
        seeking_description='Looking for shows to perform at in the San Francisco Bay Area!',
        genres=["Rock n Roll"])
    loadArtist(id=5, name='Matt Quevedo', city='New York', state='NY',
        phone="300-400-5000", 
        image_link='https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80', 
        facebook_link='https://www.facebook.com/mattquevedo923251523', 
        website_link=None,
        seeking_venue=False,
        seeking_description=None,
        genres=["Jazz"])
    loadArtist(id=6, name='The Wild Sax Band', city='San Francisco', state='CA',
        phone='432-325-5432', 
        image_link='https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80', 
        facebook_link=None, 
        website_link=None,
        seeking_venue=False,
        seeking_description=None,
        genres=["Jazz", "Classical"])
    
def loadShow(venue_id, artist_id, start_time):
    show = Show(venue_id=venue_id, artist_id=artist_id, start_time=start_time)
    db_session.add(show)
    db_session.commit()

def loadShows():
    loadShow(venue_id=1, artist_id=4, start_time='2019-05-21T21:30:00.000Z')
    loadShow(venue_id=3, artist_id=5, start_time='2019-06-15T23:00:00.000Z')
    loadShow(venue_id=3, artist_id=6, start_time='2035-04-01T20:00:00.000Z')
    loadShow(venue_id=3, artist_id=6, start_time='2035-04-08T20:00:00.000Z')
    loadShow(venue_id=3, artist_id=6, start_time='2035-04-15T20:00:00.000Z')

def setupSequences():
    engine.execute("SELECT nextval('artist_id_seq')")
    engine.execute("SELECT nextval('artist_id_seq')")
    engine.execute("SELECT nextval('artist_id_seq')")
    engine.execute("SELECT nextval('artist_id_seq')")
    engine.execute("SELECT nextval('artist_id_seq')")
    engine.execute("SELECT nextval('artist_id_seq')")
    engine.execute("SELECT nextval('venue_id_seq')")
    engine.execute("SELECT nextval('venue_id_seq')")
    engine.execute("SELECT nextval('venue_id_seq')")
    

def setupDB():
    createScheme()
    loadVenues()
    loadArtists()
    loadShows()
    setupSequences()
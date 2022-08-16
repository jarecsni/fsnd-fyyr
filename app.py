#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
import re
from unittest.result import failfast
import dateutil.parser
from datetime import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datamodels import db

# TODO clean this up
from dbsandbox import Genre, db_session, Artist, Venue, Show
from sqlalchemy.sql import func

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime


@app.route('/')
def index():
  return render_template('pages/home.html')


@app.route('/venues')
def venues():
  try: 
    result = db_session.query(Venue.id, Venue.city, Venue.state, Venue.name).order_by('state')
    city = None
    data = []
    for v in result:
      num_upcoming_shows = db_session.query(Show).filter(Show.venue_id == v.id).filter(Show.start_time > func.now()).count()
      venue = {
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": num_upcoming_shows
      }
      if v.city == city:
        data[len(data)-1].get('venues').append(venue)
      else:
        city = v.city
        data.append({
          "city": v.city,
          "state": v.state,
          "venues": [venue]
        })      
  finally:
    db_session.close()

  return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  try:
    venues = db_session.query(Venue).filter(func.lower(Venue.name).contains(func.lower(request.form.get('search_term')))).all()
    response = {
      "count": len(venues),
      "data": []
    }
    for venue in venues:
      num_upcoming_shows = 0
      for show in venue.shows:
        now = datetime.now(show.start_time.tzinfo)
        if show.start_time >= now:
          num_upcoming_shows += 1
      response.get("data").append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows
      })
  finally:
    db_session.close()

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  try:
    venue = db_session.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
      return redirect(url_for('index'))
    else:    
      past_shows = []
      upcoming_shows = []
      for show in venue.shows:
        now = datetime.now(show.start_time.tzinfo)
        if show.start_time >= now:
          upcoming_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
          })
        if show.start_time < now:
          past_shows.append({
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
          })

      data = {
        "id": venue_id,
        "name": venue.name,
        "genres": [ genre.name for genre in venue.genres ],
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows)
      }
  finally:
    db_session.close()

  return render_template('pages/show_venue.html', venue=data)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], 
      address=request.form['address'], phone=request.form['phone'], 
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'], 
      website_link=request.form['website_link'],
      seeking_talent=request.form.get('seeking_talent', 'n') == 'y', 
      seeking_description=request.form['seeking_description']
    )
    db_session.add(venue)
    db_session.commit()
  
    for genre in request.form.getlist('genres'):
      _genre = db_session.query(Genre).filter_by(name=genre).one_or_none() 
      if _genre:
        venue.genres.append(_genre)
      else:
        _genre = Genre(name=genre)
        db_session.add(_genre)
        venue.genres.append(_genre)

    db_session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    print('**** error', e)
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db_session.close()
  return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None


@app.route('/artists')
def artists():
  try:
    data = db_session.query(Artist).all()
    return render_template('pages/artists.html', artists=data)
  finally:
    db_session.close()


@app.route('/artists/search', methods=['POST'])
def search_artists():
  try:
    artists = db_session.query(Artist).filter(func.lower(Artist.name).contains(func.lower(request.form.get('search_term')))).all()
    response = {
      "count": len(artists),
      "data": []
    }
    for artist in artists:
      num_upcoming_shows = 0
      for show in artist.shows:
        now = datetime.now(show.start_time.tzinfo)
        if show.start_time >= now:
          num_upcoming_shows += 1
      response.get("data").append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": num_upcoming_shows
      })
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  finally:
    db_session.close()


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  try:
    artist = db_session.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
      return redirect(url_for('index'))
    else:    
      past_shows = []
      upcoming_shows = []
      for show in artist.shows:
        now = datetime.now(show.start_time.tzinfo)
        showDetails = {
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        }
        if show.start_time >= now:
          upcoming_shows.append(showDetails)
        if show.start_time < now:
          past_shows.append(showDetails)

      data = {
        "id": artist_id,
        "name": artist.name,
        "genres": [ genre.name for genre in artist.genres ],
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows": upcoming_shows,
        "upcoming_shows_count": len(upcoming_shows)
      }
    return render_template('pages/show_artist.html', artist=data)
  finally:
    db_session.close()


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  
  try:
    artist = db_session.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
      return redirect(url_for('index'))

    artist={
      "id": artist.id,
      "name": artist.name,
      "genres": [ genre.name for genre in artist.genres ],
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website_link": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
    }

    form = ArtistForm()
    form.name.data = artist['name']
    form.city.data = artist['city']
    form.state.data = artist['state']
    form.phone.data = artist['phone']
    form.website_link.data = artist['website_link']
    form.facebook_link.data = artist['facebook_link']
    form.image_link.data = artist['image_link']
    form.seeking_venue.data = artist['seeking_venue']
    form.seeking_description.data = artist['seeking_description']
    form.genres.data = artist['genres']

    return render_template('forms/edit_artist.html', form=form, artist=artist)
  finally:
    db_session.close()


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  try: 
    artist = db_session.query(Artist).filter(Artist.id == artist_id).first()
    
    if not artist:
      return redirect(url_for('index'))
  
    artist.name = request.form['name']
    artist.city = request.form['city']
    artist.state = request.form['state']
    artist.phone = request.form['phone']
    artist.website = request.form['website_link']
    artist.facebook_link = request.form['facebook_link']
    artist.seeking_venue = request.form.get('seeking_venue', 'n') == 'y'
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form['image_link']
    artist.genres = []
 
    for genre in request.form.getlist('genres'):
      _genre = db_session.query(Genre).filter_by(name=genre).one_or_none() 
      if _genre:
          artist.genres.append(_genre)
      else:
          _genre = Genre(name=genre)
          db_session.add(_genre)
          artist.genres.append(_genre)
    db_session.commit()
    return redirect(url_for('show_artist', artist_id=artist_id))
  except Exception as e:
    flash('Could not update artist, error', e)
    db_session.rollback()
  finally:
    db_session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  try:
    venue = db_session.query(Venue).filter(Venue.id == venue_id).first()
    if not venue:
      return redirect(url_for('index'))

    venue={
      "id": venue.id,
      "name": venue.name,
      "genres": [ genre.name for genre in venue.genres ],
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link
    }

    form = VenueForm()
    form.name.data = venue['name']
    form.address.data = venue['address']
    form.city.data = venue['city']
    form.state.data = venue['state']
    form.phone.data = venue['phone']
    form.website_link.data = venue['website_link']
    form.facebook_link.data = venue['facebook_link']
    form.image_link.data = venue['image_link']
    form.seeking_talent.data = venue['seeking_talent']
    form.seeking_description.data = venue['seeking_description']
    form.genres.data = venue['genres']

    return render_template('forms/edit_venue.html', form=form, venue=venue)
  finally:
    db_session.close()


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  try: 
    venue = db_session.query(Venue).filter(Venue.id == venue_id).first()  
    if not venue:
      return redirect(url_for('index'))

    venue.name = request.form['name']
    venue.address = request.form['address']
    venue.city = request.form['city']
    venue.state = request.form['state']
    venue.phone = request.form['phone']
    venue.website = request.form['website_link']
    venue.facebook_link = request.form['facebook_link']
    venue.seeking_talent = request.form.get('seeking_talent', 'n') == 'y'
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form['image_link']
    venue.genres = []

    for genre in request.form.getlist('genres'):
      _genre = db_session.query(Genre).filter_by(name=genre).one_or_none() 
      if _genre:
        venue.genres.append(_genre)
      else:
        _genre = Genre(name=genre)
        db_session.add(_genre)
        venue.genres.append(_genre)
    db_session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  except Exception as e:
    flash('Could not update venue, error', e)
    db_session.rollback()
  finally:
    db_session.close()


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
    artist = Artist(name=request.form['name'], city=request.form['city'], state=request.form['state'], 
      phone=request.form['phone'], 
      image_link=request.form['image_link'],
      facebook_link=request.form['facebook_link'], 
      website_link=request.form['website_link'],
      seeking_venue=request.form.get('seeking_venue', 'n') == 'y', 
      seeking_description=request.form['seeking_description']
    )
    db_session.add(artist)
    db_session.commit()
  
    for genre in request.form.getlist('genres'):
      _genre = db_session.query(Genre).filter_by(name=genre).one_or_none() 
      if _genre:
        artist.genres.append(_genre)
      else:
        _genre = Genre(name=genre)
        db_session.add(_genre)
        artist.genres.append(_genre)
          
    db_session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception as e:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally: 
    db_session.close()
  
  return render_template('pages/home.html')


@app.route('/shows')
def shows():
  try:
    shows = db_session.query(Show).all();
    data = []
    for show in shows:
      data.append({
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": str(show.start_time)
      })

    return render_template('pages/shows.html', shows=data)
  finally:
    db_session.close()


@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
    show = Show(
      artist_id = request.form['artist_id'],
      venue_id = request.form['venue_id'],
      start_time = request.form['start_time']
    )
    db_session.add(show)
    db_session.commit()
    flash('Show was successfully listed!')
    return render_template('pages/home.html')
  except Exception as e:
    print('error creating new show', e)
    flash('An error occurred. Show could not be listed.')
  finally: 
    db_session.close()


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Note: localhost:5000 won't work on new macOS (only 127.0.0.1:5000)
if __name__ == '__main__':
    app.run(port=os.environ.get('PORT', 5000))

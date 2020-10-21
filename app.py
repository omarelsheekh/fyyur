#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import datetime
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,abort
from sqlalchemy.orm import query
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm as Form
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
migrate=Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='venue')

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # implement any missing fields, as a database migration using Flask-Migrate
    shows = db.relationship('Show', backref='artist')

# Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  datetime = db.Column(db.String, nullable=False)
  artist_id = db.Column(db.Integer , db.ForeignKey('Artist.id'),nullable=False)
  venue_id = db.Column(db.Integer , db.ForeignKey('Venue.id'),nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  class Area:
    def __init__(self,state,city,venues):
      self.state=state
      self.city=city
      self.venues=venues
  areas=[]

  q=Venue.query.order_by('state','city').all()
  for v in q:
    if len(areas)==0:
      areas.append(Area(v.state,v.city,[]))
    elif not (areas[len(areas)-1].state==v.state and areas[len(areas)-1].city == v.city):
        areas.append(Area(v.state,v.city,[]))
    areas[len(areas)-1].venues.append(v)

  return render_template('pages/venues.html', areas=areas)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  word=request.form.get('search_term', '')
  response=Venue.query.filter(Venue.name.ilike('%{}%'.format(word)))
  return render_template('pages/search_venues.html', results=response, search_term=word)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  venue=Venue.query.get(venue_id)
  if venue is not None:
    upcoming_shows=[]
    past_shows=[]
    now=dateutil.parser.parse(str(datetime.now()))
    for show in venue.shows:
      show_date=dateutil.parser.parse(show.datetime)
      if now >= show_date:
        past_shows.append(show)
      else:
        upcoming_shows.append(show)
    return render_template('pages/show_venue.html',len=len, past_shows=past_shows, upcoming_shows=upcoming_shows, venue=venue)
  else:
    abort(404)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  try:
    venue=Venue(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      address=request.form.get('address'),
      phone=request.form.get('phone'),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link')
    )
    db.session.add(venue)
    db.session.commit()
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue= Venue.query.filter_by(id=venue_id)
    if venue.first() is not None:
      venue.delete()
      db.session.commit()
      # on successful db delete, flash success
      flash('Venue was successfully DELETED!')
    else:
      abort(404)
  except:
    db.session.rollback()
    # on unsuccessful db delete, flash an error instead.
    flash('An error occurred. Venue could not be DELETED.')

  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # replace with real data returned from querying the database
  artists= Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  word=request.form.get('search_term', '')
  response=Artist.query.filter(Artist.name.ilike('%{}%'.format(word)))
  return render_template('pages/search_artists.html', results=response, search_term=word)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # replace with real venue data from the venues table, using venue_id
  artist=Artist.query.get(artist_id)
  if artist is not None:
    upcoming_shows=[]
    past_shows=[]
    now=dateutil.parser.parse(str(datetime.now()))
    for show in artist.shows:
      show_date=dateutil.parser.parse(show.datetime)
      if now >= show_date:
        past_shows.append(show)
      else:
        upcoming_shows.append(show)
    return render_template('pages/show_artist.html', len=len, artist=artist, past_shows=past_shows, upcoming_shows=upcoming_shows)
  else:
    abort(404)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist=Artist.query.get(artist_id)
  if artist is not None:
    # populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
    abort(404)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=Artist.query.get(artist_id)
  if artist is not None:
    artist.name=request.form.get('name'),
    artist.city=request.form.get('city'),
    artist.state=request.form.get('state'),
    artist.phone=request.form.get('phone'),
    artist.genres=','.join(request.form.getlist('genres')),
    artist.facebook_link=request.form.get('facebook_link'),
    artist.image_link=request.form.get('image_link')
    try:
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be Updated.')
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    abort(404)
  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue=Venue.query.get(venue_id)
  if venue is not None:
    # populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  else:
    abort(404)
  

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue= Venue.query.get(venue_id)
  if venue is not None:
    try:
      venue.name=request.form.get('name'),
      venue.city=request.form.get('city'),
      venue.state=request.form.get('state'),
      venue.address=request.form.get('address'),
      venue.phone=request.form.get('phone'),
      venue.image_link=request.form.get('image_link'),
      venue.facebook_link=request.form.get('facebook_link')
      db.session.commit()
      # on successful db update, flash success
      flash('Venue ' + request.form['name'] + ' was successfully Updated!')
    except:
      db.session.rollback()
      # on unsuccessful db update, flash an error instead.
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be Updated.')
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    abort(404)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Venue record in the db, instead
  # modify data to be the data object returned from db insertion
  try:
    artist=Artist(
      name=request.form.get('name'),
      city=request.form.get('city'),
      state=request.form.get('state'),
      phone=request.form.get('phone'),
      genres=','.join(request.form.getlist('genres')),
      facebook_link=request.form.get('facebook_link'),
      image_link=request.form.get('image_link')
    )
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows=Show.query.all()
  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  artist=Artist.query.get(request.form.get('artist_id'))
  venue=Venue.query.get(request.form.get('venue_id'))
  if artist and venue:
    try:
      show=Show(
        artist_id=request.form.get('artist_id'),
        venue_id=request.form.get('venue_id'),
        datetime= format_datetime(request.form.get('start_time'))
      )
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
  else:
    flash('Artist or Venue id is not valid')
  return render_template('pages/home.html')

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

# Default port:
if __name__ == '__main__':
    app.run(debug=False)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

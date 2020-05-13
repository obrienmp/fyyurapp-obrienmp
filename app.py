#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
import re
from datetime import datetime
from logging import Formatter, FileHandler
from flask_wtf import Form
from wtforms.validators import ValidationError
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

def validPhone(number):
    regex = r'\w{3}-\w{3}-\w{4}'
    msgFormat = 'Not a valid phone number. Phone numbers must be 333-222-1111.'
    msgLength = 'Not a valid phone number. Phone numbers should be 10 digits with dashes (-).'
    match = re.match(regex, str(number))
    if (match is None and str(number) != ''):
        message = msgFormat
        raise ValidationError(message)
    elif len(str(number)) > 12:
        message = msgLength
        raise ValidationError(message)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    seeking_talent = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    venue_shows = db.relationship('Show', backref='venue_shows', lazy=True)

    def __repr__(self):
          return f'<Venue {self.id} {self.name}>'
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(120))
    artist_shows = db.relationship('Show', backref='artist_shows', lazy=True)

    def __repr__(self):
          return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
      __tablename__ = 'show'

      id = db.Column(db.Integer, primary_key=True)
      artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), nullable=False)
      venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), nullable=False)
      start_time = db.Column(db.DateTime, nullable=False)

      def __repr__(self):
        return f'<Show {self.id} {self.start_time}>'

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
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  venues = Venue.query.all()
  locations = set()
  for venue in venues:
    locations.add((venue.city,venue.state))
  for location in locations:
    data.append({
      "city": location[0],
      "state": location[1],
      "venues": []
    })
  for venue in venues:
    num_shows = 0
    for entry in data:
      if entry['city'] == venue.city and entry['state'] == venue.state:
        entry['venues'].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': num_shows
        })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  venues = Venue.query.filter(Venue.name.ilike('%' + request.form.get('search_term') + '%')).all()
  response = {
    "count": len(venues),
    "data": venues
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  ## shows the venue page with the given venue_id
  ## TODO: replace with real venue data from the venues table, using venue_id
  data = Venue.query.filter_by(id=venue_id).outerjoin(Show).order_by('start_time').outerjoin(Artist).one()
  upcoming_shows = []
  past_shows = []
  for show in data.venue_shows:
    if show.start_time >= datetime.now():
      upcoming_shows.append({
        "artist_image_link": show.artist_shows.image_link,
        "artist_id": show.artist_id,
        "artist_name": show.artist_shows.name,
        "start_time": format_datetime(str(show.start_time))})
    elif show.start_time < datetime.now():
      past_shows.append({
        "artist_image_link": show.artist_shows.image_link,
        "artist_id": show.artist_id,
        "artist_name": show.artist_shows.name,
        "start_time": format_datetime(str(show.start_time))})
    else:
      print('show not processed')
  data.upcoming_shows_count = len(upcoming_shows)
  data.upcoming_shows = upcoming_shows
  data.past_shows_count = len(past_shows)
  data.past_shows = past_shows

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  try:
    validPhone(request.form['phone'])
    venue = Venue(name=request.form['name'],
      city=request.form['city'], state=request.form['state'],
      address=request.form['address'], phone=request.form['phone'],
      genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link'],
      website=request.form['website'],
      seeking_talent=request.form['seeking_talent'],
      seeking_description=request.form['seeking_description'])
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except ValidationError as e:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed. ' + str(e))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    name = Venue.query.filter_by(id=venue_id).one().name
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue ' + name + ' was successfully deleted!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Venue ' + name + ' could not be deleted!')
  finally:
    db.session.close()
  
  return jsonify({'success': True})
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
    # return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data = Artist.query.order_by('id').all()
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  ## TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  ## seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  ## search for "band" should return "The Wild Sax Band".
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  artists = Artist.query.filter(Artist.name.ilike('%' + request.form.get('search_term') + '%')).all()
  response = {
    "count": len(artists),
    "data": artists
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  ## shows the venue page with the given venue_id
  ## TODO: replace with real venue data from the venues table, using venue_id
  data = Artist.query.filter_by(id=artist_id).outerjoin(Show).order_by(Show.start_time).outerjoin(Venue).one()
  upcoming_shows = []
  past_shows = []
  for show in data.artist_shows:
    if show.start_time >= datetime.now():
      upcoming_shows.append({
        "venue_image_link": show.venue_shows.image_link,
        "venue_id": show.venue_id,
        "venue_name": show.venue_shows.name,
        "start_time": format_datetime(str(show.start_time))})
    elif show.start_time < datetime.now():
      past_shows.append({
        "venue_image_link": show.venue_shows.image_link,
        "venue_id": show.venue_id,
        "venue_name": show.venue_shows.name,
        "start_time": format_datetime(str(show.start_time))})
    else:
      print('show not processed')
  data.upcoming_shows_count = len(upcoming_shows)
  data.upcoming_shows = upcoming_shows
  data.past_shows_count = len(past_shows)
  data.past_shows = past_shows

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter_by(id=artist_id).one()
  form = ArtistForm(
    name = artist.name,
    city = artist.city,
    state = artist.state,
    phone = artist.phone,
    genres = artist.genres,
    facebook_link = artist.facebook_link,
    website = artist.website,
    seeking_venue = artist.seeking_venue,
    seeking_description = artist.seeking_description
  )

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  # print(request.form['seeking_venues'])
  # print(bool(request.form['seeking_venues']))
  try:
    validPhone(request.form['phone'])
    artist = {
      "name": request.form['name'],
      "city": request.form['city'], "state": request.form['state'],
      "phone": request.form['phone'], "genres": request.form.getlist('genres'),
      "facebook_link": request.form['facebook_link'],
      "website": request.form['website'],
      "seeking_venue": bool(request.form['seeking_venue']),
      "seeking_description": request.form['seeking_description']}
    Artist.query.filter_by(id=artist_id).update(artist)
    db.session.commit()
  except ValidationError as e:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated ' + str(e))
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  venue = Venue.query.filter_by(id=venue_id).one()
  form = VenueForm(
    name = venue.name,
    city = venue.city,
    state = venue.state,
    address = venue.address,
    phone = venue.phone,
    genres = venue.genres,
    facebook_link =  venue.facebook_link,
    website = venue.website,
    seeking_talent = venue.seeking_talent,
    seeking_description = venue.seeking_description
  )

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    validPhone(request.form['phone'])
    venue = {
      "name": request.form['name'],
      "city": request.form['city'], "state": request.form['state'],
      "address": request.form['address'], "phone": request.form['phone'],
      "genres": request.form.getlist('genres'),
      "facebook_link": request.form['facebook_link'],
      "website": request.form['website'],
      "seeking_talent": bool(request.form['seeking_talent']),
      "seeking_description": request.form['seeking_description']
    }
    Venue.query.filter_by(id=venue_id).update(venue)
    db.session.commit()
  except ValidationError as e:
    db.session.rollback()
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated ' + str(e))
  except:
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  try:
    validPhone(request.form['phone'])
    artist = Artist(name=request.form['name'],
      city=request.form['city'],state=request.form['state'],
      phone=request.form['phone'],genres=request.form.getlist('genres'),
      facebook_link=request.form['facebook_link'], website=request.form['website'],
      seeking_venue=bool(request.form['seeking_venue']),
      seeking_description=request.form['seeking_description'])
    # print(artist)
    db.session.add(artist)
    db.session.commit()
    # print(Artist.query.all())
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except ValidationError as e:
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' phone number could not be updated ' + str(e))
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
    db.session.close()

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  # return 'done'
  return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  try:
    name = Artist.query.filter_by(id=artist_id).one().name
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
    flash('Artist ' + name + ' was successfully deleted!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. Artist ' + name + ' could not be deleted!')
  finally:
    db.session.close()
  
  return jsonify({'success': True})

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  ## displays list of shows at /shows
  ## TODO: replace with real venues data.
  ##       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.join("artist_shows").join("venue_shows").order_by(Show.start_time).all()
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue_shows.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist_shows.name,
      "artist_image_link": show.artist_shows.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # error = False
  try:
    show = Show(
      artist_id=request.form['artist_id'],
      venue_id=request.form['venue_id'],
      start_time=request.form['start_time'])
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
    # error = True
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

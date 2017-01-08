# coding: utf-8

import flask

import config

from main import app

import auth
import model
from urlparse import urlparse
from google.appengine.ext import blobstore
import pdb
###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
    return make_home_template(isEditMode=False)

# todo, securetodo: check if hostname matches user registerd
@app.route('/edit')
@auth.admin_required
def edit():
  return make_home_template(isEditMode=True)

def make_home_template(isEditMode):
    parsed_request = urlparse(flask.request.url)
    hostname = parsed_request.hostname
    if 'www.' in hostname:
        hostname = hostname.split('www.')[1]

    # get carousel resources
    query = model.Album.query(
        model.Album.hostname==hostname,
        model.Album.isCarousel==True
    )
    carousel_album_db = query.get()

    if not carousel_album_db and isEditMode:
        carousel_album_db = model.Album(
            user_key=auth.current_user_key(),
            hostname=hostname,
            isCarousel=True
        )
        carousel_album_db.put()

    carousel_resource_dbs = None
    if carousel_album_db:
        carousel_resource_dbs, cursors = carousel_album_db.get_resource_dbs()

    # get site albums
    query = model.Album.query(
      model.Album.hostname==hostname,
      model.Album.isCarousel==False
    )
    album_dbs = query.fetch(30) # limit site albums to 30
    album_list = []
    for album_db in album_dbs:
        query = model.Resource.query(
          model.Resource.album_key==album_db.key
        )
        album_image_db = query.get()
        if album_image_db:
            album_info = {'album_db': album_db, 'image_url': album_image_db.image_url}
        else:
            album_info = {'album_db': album_db, 'image_url': None}
        album_list.append(album_info)

    get_upload_url = None
    if carousel_album_db and isEditMode:
        get_upload_url=flask.url_for('api.album.resource.upload', key=carousel_album_db.key.urlsafe())

    return flask.render_template(
        'welcome.html',
        html_class='welcome',
        isEditMode=isEditMode,
        album_list=album_list,
        carousel_resource_dbs=carousel_resource_dbs,
        get_upload_url=get_upload_url,
        has_json=True,
        upload_url=blobstore.create_upload_url(
          flask.request.path,
          gs_bucket_name=config.CONFIG_DB.bucket_name or None,
        ),
    )

###############################################################################
# Sitemap stuff
###############################################################################
@app.route('/sitemap.xml')
def sitemap():
  response = flask.make_response(flask.render_template(
    'sitemap.xml',
    lastmod=config.CURRENT_VERSION_DATE.strftime('%Y-%m-%d'),
  ))
  response.headers['Content-Type'] = 'application/xml'
  return response


###############################################################################
# Warmup request
###############################################################################
@app.route('/_ah/warmup')
def warmup():
  # TODO: put your warmup code here
  return 'success'

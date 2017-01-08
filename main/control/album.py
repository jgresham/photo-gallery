# coding: utf-8

import urllib

from google.appengine.ext import blobstore
import flask
import flask_wtf
import wtforms

import auth
import config
import model
import util

from main import app

from urlparse import urlparse
import pdb

###############################################################################
# Upload
###############################################################################
@app.route('/album/create')
@auth.admin_required
def album_create():
    # album_db = model.Album.get_by_id(album_id)
    #
    # if album_db
    #     if album_db.user_key != auth.current_user_key():
    #         return flask.abort(404)
    #     else:
    #         resource_dbs = album_db.get_resource_dbs()
    #
    # if not album_db:
    # todo, securetodo: check if user is registerd with hostname>?
    parsed_request = urlparse(flask.request.url)
    hostname = parsed_request.hostname
    if 'www.' in hostname:
        hostname = hostname.split('www.')[1]
    album_db = model.Album(
        user_key=auth.current_user_key(),
        hostname=hostname
    )
    album_db.put()
    return flask.redirect(flask.url_for(
      'album_update', album_id=album_db.key.id(),
    ))
    # return flask.render_template(
    #   'album/album_upload.html',
    #   title='Album Upload',
    #   html_class='album-upload',
    #   get_upload_url=flask.url_for('api.album.resource.upload', key=album_db.key.urlsafe()),
    #   has_json=True,
    #   upload_url=blobstore.create_upload_url(
    #     flask.request.path,
    #     gs_bucket_name=config.CONFIG_DB.bucket_name or None,
    #   ),
    #   album_db=album_db,
    #   resource_dbs=resource_dbs,
    # )

@app.route('/album/create/carousel')
@auth.admin_required
def album_create_carousel():
    parsed_request = urlparse(flask.request.url)
    hostname = parsed_request.hostname
    if 'www.' in hostname:
        hostname = hostname.split('www.')[1]
        
    query = model.Album.query(
      ndb.AND(
        user_key==auth.current_user_key(),
        hostname==hostname,
        isCarousel==True
      )
    )
    album_db = query.fetch(1)

    if album_db:
        if album_db.user_key != auth.current_user_key():
            return flask.abort(404)
        else:
            resource_dbs = album_db.get_resource_dbs()

    if not album_db:
        album_db = model.Album(
            user_key=auth.current_user_key(),
            hostname=hostname,
            isCarousel=True
        )
        album_db.put()
        return flask.redirect(flask.url_for(
          'album_update', album_id=album_db.key.id(),
        ))

###############################################################################
# List
###############################################################################
# @app.route('/album/', endpoint='album_list')
# @auth.login_required
# def resource_list():
#   resource_dbs, resource_cursor = auth.current_user_db().get_resource_dbs()
#
#   return flask.render_template(
#     'resource/resource_list.html',
#     html_class='resource-list',
#     title='Resource List',
#     resource_dbs=resource_dbs,
#     next_url=util.generate_next_url(resource_cursor),
#     api_url=flask.url_for('api.resource.list'),
#   )


###############################################################################
# View
###############################################################################
@app.route('/album/<int:album_id>/', endpoint='album_view')
def album_view(album_id):
  album_db = model.Album.get_by_id(album_id)

  if not album_db:
    return flask.abort(404)

  resource_dbs, cursors = album_db.get_resource_dbs()
  return flask.render_template(
    'album/album_view.html',
    html_class='album-view',
    title='%s' % (album_db.name),
    album_db=album_db,
    resource_dbs=resource_dbs,
  )

###############################################################################
# Update
###############################################################################
class AlbumUpdateForm(flask_wtf.FlaskForm):
  name = wtforms.TextField('Name', [wtforms.validators.required()])
  description = wtforms.TextField('Description', [wtforms.validators.required()])
  albumType = wtforms.TextField('Type of album')

@app.route('/album/<int:album_id>/update/', methods=['GET', 'POST'], endpoint='album_update')
@auth.admin_required
def album_update(album_id):
  album_db = model.Album.get_by_id(album_id)

  if not album_db or album_db.user_key != auth.current_user_key():
    return flask.abort(404)

  form = AlbumUpdateForm(obj=album_db)

  if form.validate_on_submit():
    form.populate_obj(album_db)
    album_db.put()
    return flask.redirect(flask.url_for(
      'album_view', album_id=album_db.key.id(),
    ))

  resource_dbs, cursors = album_db.get_resource_dbs()
  return flask.render_template(
    'album/album_update.html',
    html_class='album-update',
    title='%s' % (album_db.name),
    album_db=album_db,
    form=form,
    resource_dbs=resource_dbs,
    get_upload_url=flask.url_for('api.album.resource.upload', key=album_db.key.urlsafe()),
    has_json=True,
    upload_url=blobstore.create_upload_url(
      flask.request.path,
      gs_bucket_name=config.CONFIG_DB.bucket_name or None,
    ),
    # api_url=flask.url_for('api.album.resource.upload', key=album_db.key.urlsafe()),
  )

###############################################################################
# Download
###############################################################################
# @app.route('/resource/<int:resource_id>/download/')
# @auth.login_required
# def resource_download(resource_id):
#   resource_db = model.Resource.get_by_id(resource_id)
#   if not resource_db or resource_db.user_key != auth.current_user_key():
#     return flask.abort(404)
#   name = urllib.quote(resource_db.name.encode('utf-8'))
#   url = '/serve/%s?save_as=%s' % (resource_db.blob_key, name)
#   return flask.redirect(url)

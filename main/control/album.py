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
import cloudstorage as gcs

###############################################################################
# Upload
###############################################################################
@app.route('/album/<int:album_id>/edit')
@auth.login_required
def album_edit(album_id):
    album_db = model.Album.get_by_id(album_id)

    if album_db
        if album_db.user_key != auth.current_user_key():
            return flask.abort(404)
        else:
            resource_dbs = album_db.get_resource_dbs()

    if not album_db:
        album_db = model.Album(user_key=auth.current_user_key())
        album_db.put()

    return flask.render_template(
      'album/album_upload.html',
      title='Album Upload',
      html_class='album-upload',
      get_upload_url=flask.url_for('api.album.resource.upload', key=album_db.key.urlsafe()),
      has_json=True,
      upload_url=blobstore.create_upload_url(
        flask.request.path,
        gs_bucket_name=config.CONFIG_DB.bucket_name or None,
      ),
      album_db=album_db,
      resource_dbs=resource_dbs,
    )


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

  if album_db
      if album_db.user_key != auth.current_user_key():
          return flask.abort(404)
      else:
          resource_dbs = album_db.get_resource_dbs()
  if not resource_db or resource_db.user_key != auth.current_user_key():
    return flask.abort(404)

  return flask.render_template(
    'album/album_view.html',
    html_class='album-view',
    title='%s' % (album_db.name or 'Album'),
    album_db=album_db,
    resource_dbs=resource_dbs,
    api_url=flask.url_for('api.album', key=album_db.key.urlsafe()),
  )
###############################################################################
# Update
###############################################################################
class ResourceUpdateForm(flask_wtf.FlaskForm):
  name = wtforms.TextField('Name', [wtforms.validators.required()])


@app.route('/resource/<int:resource_id>/update/', methods=['GET', 'POST'], endpoint='resource_update')
@auth.login_required
def resource_update(resource_id):
  resource_db = model.Resource.get_by_id(resource_id)

  if not resource_db or resource_db.user_key != auth.current_user_key():
    return flask.abort(404)

  form = ResourceUpdateForm(obj=resource_db)

  if form.validate_on_submit():
    form.populate_obj(resource_db)
    resource_db.put()
    return flask.redirect(flask.url_for(
      'resource_view', resource_id=resource_db.key.id(),
    ))

  return flask.render_template(
    'resource/resource_update.html',
    html_class='resource-update',
    title='%s' % (resource_db.name),
    resource_db=resource_db,
    form=form,
    api_url=flask.url_for('api.resource', key=resource_db.key.urlsafe()),
  )


###############################################################################
# Download
###############################################################################
@app.route('/resource/<int:resource_id>/download/')
@auth.login_required
def resource_download(resource_id):
  resource_db = model.Resource.get_by_id(resource_id)
  if not resource_db or resource_db.user_key != auth.current_user_key():
    return flask.abort(404)
  name = urllib.quote(resource_db.name.encode('utf-8'))
  url = '/serve/%s?save_as=%s' % (resource_db.blob_key, name)
  return flask.redirect(url)

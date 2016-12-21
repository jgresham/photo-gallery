# coding: utf-8

from __future__ import absolute_import

from google.appengine.api import images
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
import flask
import flask_restful
import werkzeug

from api import helpers
import auth
import config
import model
import util
import pdb

from main import api_v1


###############################################################################
# Endpoints
###############################################################################
# @api_v1.resource('/resource/', endpoint='api.resource.list')
# class ResourceListAPI(flask_restful.Resource):
#   @auth.admin_required
#   def get(self):
#     resource_keys = util.param('resource_keys', list)
#     if resource_keys:
#       resource_db_keys = [ndb.Key(urlsafe=k) for k in resource_keys]
#       resource_dbs = ndb.get_multi(resource_db_keys)
#       return helpers.make_response(resource_dbs, model.Resource.FIELDS)
#
#     resource_dbs, next_cursor = model.Resource.get_dbs()
#     return helpers.make_response(
#         resource_dbs, model.Resource.FIELDS, next_cursor,
#       )
#
#   @auth.admin_required
#   def delete(self):
#     resource_keys = util.param('resource_keys', list)
#     if not resource_keys:
#       helpers.make_not_found_exception(
#           'Resource(s) %s not found' % resource_keys
#         )
#     resource_db_keys = [ndb.Key(urlsafe=k) for k in resource_keys]
#     delete_resource_dbs(resource_db_keys)
#     return flask.jsonify({
#         'result': resource_keys,
#         'status': 'success',
#       })


@api_v1.resource('/album/<string:key>/', endpoint='api.album')
class AlbumAPI(flask_restful.Resource):
  def get(self, key):
    album_db = ndb.Key(urlsafe=key).get()
    if not album_db:
      helpers.make_not_found_exception('Album %s not found' % key)
    return helpers.make_response(album_db, model.Album.FIELDS)

  @auth.login_required
  def delete(self, key):
    album_db = ndb.Key(urlsafe=key).get()
    if not album_db or album_db.user_key != auth.current_user_key():
      helpers.make_not_found_exception('Album %s not found' % key)
    resource_dbs, cursors = album_db.get_resource_dbs()
    delete_resource_dbs(resource_dbs)
    delete_album_key(album_db.key)
    return helpers.make_response(album_db, model.Album.FIELDS)


@api_v1.resource('/album/<string:key>/resource/upload/', endpoint='api.album.resource.upload')
class AlbumResourceUploadAPI(flask_restful.Resource):
  @auth.login_required
  def get(self, key):
    count = util.param('count', int) or 1
    urls = []
    for i in range(count):
      urls.append({'upload_url': blobstore.create_upload_url(
          flask.request.path,
          gs_bucket_name=config.CONFIG_DB.bucket_name or None,
        )})
    return flask.jsonify({
        'status': 'success',
        'count': count,
        'result': urls,
      })

  @auth.login_required
  def post(self, key):
    album_db = ndb.Key(urlsafe=key).get()
    if album_db and album_db.user_key == auth.current_user_key():
        resource_db = resource_db_from_upload(album_db=album_db)
        if resource_db:
          return helpers.make_response(resource_db, model.Resource.FIELDS)
    flask.abort(500)


###############################################################################
# Helpers
###############################################################################
# @ndb.transactional(xg=True)
# def delete_resource_dbs(resource_db_keys):
#   for resource_key in resource_db_keys:
#     delete_resource_key(resource_key)


# def delete_resource_key(resource_key):
#   resource_db = resource_key.get()
#   if resource_db:
#     blobstore.BlobInfo.get(resource_db.blob_key).delete()
#     resource_db.key.delete()

@ndb.transactional(xg=True)
def delete_album_key(album_key):
  album_db = album_key.get()
  if album_db:
    album_db.key.delete()

def delete_resource_dbs(resource_dbs):
  for resource_db in resource_dbs:
    delete_resource_db(resource_db)


def delete_resource_db(resource_db):
  if resource_db:
    blobstore.BlobInfo.get(resource_db.blob_key).delete()
    resource_db.key.delete()

def resource_db_from_upload(album_db):
  try:
    uploaded_file = flask.request.files['file']
  except:
    return None
  headers = uploaded_file.headers['Content-Type']
  blob_info_key = werkzeug.parse_options_header(headers)[1]['blob-key']
  blob_info = blobstore.BlobInfo.get(blob_info_key)

  image_url = None
  if blob_info.content_type.startswith('image'):
    try:
      image_url = images.get_serving_url(blob_info.key())
    except:
      pass

  resource_db = model.Resource(
      album_key=album_db.key,
      user_key=auth.current_user_key(),
      blob_key=blob_info.key(),
      name=blob_info.filename,
      content_type=blob_info.content_type,
      size=blob_info.size,
      image_url=image_url,
      bucket_name=config.CONFIG_DB.bucket_name or None,
    )
  resource_db.put()
  return resource_db

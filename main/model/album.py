# coding: utf-8

from __future__ import absolute_import

from google.appengine.ext import ndb
import flask

from api import fields
import model
import util


class Album(model.Base):
  user_key = ndb.KeyProperty(kind=model.User, required=True)
  name = ndb.StringProperty()
  description = ndb.StringProperty()

  FIELDS = {
    'name': fields.String,
    'description': fields.String
  }

  def get_resource_dbs(self, **kwargs):
    return model.Resource.get_dbs(album_key=self.key, **kwargs)

  FIELDS.update(model.Base.FIELDS)

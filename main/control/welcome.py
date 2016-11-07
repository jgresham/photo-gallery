# coding: utf-8

import flask

import config

from main import app

###############################################################################
# Welcome
###############################################################################
@app.route('/')
def welcome():
    return make_home_template(isEditMode=False)

@app.route('/edit')
def edit():
  return make_home_template(isEditMode=True)

def make_home_template(isEditMode):
    
    return flask.render_template(
        'welcome.html',
        html_class='welcome',
        isEditMode=isEditMode)

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

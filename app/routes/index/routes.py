import os
import json
import bleach
import binascii
import logging

from . import _ as bp, logging

from uuid import uuid4
from flask import (current_app as app,
				   render_template,
				   request,
				   Response,
				   redirect,
				   session,
				   url_for,
				   flash,
				   abort)

@bp.route("/", methods=['GET', 'POST'])
def index():
	logging.info(session.sid)
	if not session.sid in session:
		session['sid'] = session.sid
	return render_template('index.html')

@bp.route("/terminate", methods=['GET', 'POST'])
def terminate():
	if response := Response(json.dumps({}), 200):
		if session := app.config.get('SESSION_COOKIE_NAME'):
			response.delete_cookie(session, path='/')
		return response
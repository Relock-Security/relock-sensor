import os 

import logging
import redis

from flask import Flask, url_for

from flask_session import Session
from flask_bootstrap import Bootstrap5 as Bootstrap

from datetime import timedelta

bootstrap = Bootstrap()
session = Session()

def init_app(*args, **kwargs):

	""" Initialize the core application. """
	app = Flask(__name__, instance_relative_config=False)

	""" Core server settings """
	app.config.update(
		SERVER_HSTS = 'https' if int(kwargs.get('port', 443)) else 'http',
		SERVER_HOST = str(kwargs.get('host')),
		SERVER_BIND = str(kwargs.get('ip')),
		SERVER_PORT = int(kwargs.get('port', 443)),
		APP_DEBUG   = bool(kwargs.get('debug', False))
	)

	""" Flask_Session configuration """
	app.config.update(
		REDIS_HOST = os.environ.get('REDIS_HOST', '172.17.0.2'),
		REDIS_PORT = os.environ.get('REDIS_PORT', 6379),
		REDIS_DB   = os.environ.get('REDIS_DB', 0)
	)

	""" Relock_Host configuration """
	app.config.update(
		RELOCK_HOST = os.environ.get('RELOCK_HOST'),
	)

	""" Flask_Session configuration """
	app.config.update(
		SESSION_COOKIE_DOMAIN = None,
		SESSION_COOKIE_PATH = '/',
		SESSION_COOKIE_NAME = 'session',
		SESSION_COOKIE_HTTPONLY = True,
		SESSION_COOKIE_SECURE = True,
		SESSION_COOKIE_SAMESITE = 'lax',
		SESSION_USE_SIGNER = True,
		SESSION_PROTECTION = 'strong',
		SESSION_PERMANENT = False,
		SESSION_REFRESH_EACH_REQUEST = False,
		PERMANENT_SESSION_LIFETIME = timedelta(hours=30),
		REMEMBER_ME = False,
		#REMEMBER_COOKIE_DURATION = timedelta(days=30),
		REMEMBER_COOKIE_SECURE = True
	)

	app.config.update(
		SESSION_TYPE  = 'redis',
		SESSION_REDIS = redis.Redis(host=app.config.get('REDIS_HOST'), 
								    port=app.config.get('REDIS_PORT'), 
								    db=app.config.get('REDIS_DB'), )
	)
	
	app.config.update(
		SECRET_KEY = 'very_very_secret_key'
	)

	with app.app_context() as context:

		""" Initialize extensions """
		session.init_app(app)
		bootstrap.init_app(app)
		
		""" Load endpoints """		
		from .routes.index import _; app.register_blueprint(_)

		""" Load App contexts """
		from .contexts import (request_nonce_processor,
							   after_request,
							   preflight,
							   ico)

		logging.info('Sample App started.')
	return app


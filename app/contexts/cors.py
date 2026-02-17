import os
import base64
import logging

from flask import (current_app as app, 
				   send_from_directory,
				   request,
				   Response,
				   session,
				   redirect,
				   url_for,
				   abort)

@app.context_processor
def request_nonce_processor():
	def request_nonce():
		if not hasattr(request, '__nonce'):
			setattr(request, '__nonce', base64.urlsafe_b64encode(os.urandom(8)).decode())
		return getattr(request, '__nonce')
	return dict(request_nonce=request_nonce)

@app.after_request
def after_request(response):
	if request.path == '/favicon.ico':
		return response

	allowed_origin = 'https://' + app.config.get('RELOCK_HOST')
	origin = request.headers.get('Origin', '')

	# CORS: only reflect/allow the expected origin (avoid wildcard with credentials)
	if origin and origin == allowed_origin:
		response.headers.set('Access-Control-Allow-Origin', origin)
		response.headers.set('Access-Control-Allow-Credentials', 'true')
	else:
		# If you want to hard-fail cross-origin, you can omit ACAO entirely.
		# Keeping it omitted is safest.
		pass

	# Ensure caches vary by Origin (and by request headers/method for preflight)
	vary_parts = set()
	if 'Vary' in response.headers:
		for part in response.headers.get('Vary', '').split(','):
			part = part.strip()
			if part:
				vary_parts.add(part)

	vary_parts.update({'Origin', 'Access-Control-Request-Method', 'Access-Control-Request-Headers'})
	response.headers.set('Vary', ', '.join(sorted(vary_parts)))

	# Security headers
	if 'Cross-Origin-Resource-Policy' not in response.headers:
		response.headers.set('Cross-Origin-Resource-Policy', 'same-origin')
	if 'Cross-Origin-Opener-Policy' not in response.headers:
		response.headers.set('Cross-Origin-Opener-Policy', 'same-origin')

	response.headers.set('X-Frame-Options', 'DENY')
	response.headers.set('X-Content-Type-Options', 'nosniff')
	response.headers.set('X-Permitted-Cross-Domain-Policies', 'none')
	response.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')

	# Pick ONE Referrer-Policy value
	response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin')

	# CORS allowlists
	response.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
	response.headers.set(
		'Access-Control-Allow-Headers',
		'Origin, Accept, X-Requested-With, X-Key-Token, X-Key-Signature, X-Key-Data, '
		'X-Key-Device, X-Key-Session, X-Key-Time, X-Key-Stamp, X-Key-Wildcard, '
		'Accept-Language, Content-Type, Accept-Encoding, Upgrade-Insecure-Requests'
	)

	# Expose only what you need (no wildcard when credentials are used)
	response.headers.set('Access-Control-Expose-Headers', 'Authorization, Content-Type')
	response.headers.set('Access-Control-Max-Age', '600')

	# Optional: Private Network Access (only if requested by browser)
	if request.headers.get('Access-Control-Request-Private-Network') == 'true':
		response.headers.set('Access-Control-Allow-Private-Network', 'true')

	# Branding (note: some servers overwrite these)
	response.headers.set('Server', 're:lock')
	response.headers.set('X-Powered-By', 're:lock')

	# CSP (kept close to your original; consider removing 'unsafe-eval' if possible)
	nonce = getattr(request, '__nonce', '')
	response.headers.set(
		'Content-Security-Policy',
		"default-src 'self' 'unsafe-eval'; "
		"connect-src 'self' https://*."+ app.config.get('RELOCK_HOST') +" https://fonts.gstatic.com https://fonts.googleapis.com "
		"https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
		f"style-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com https://fonts.googleapis.com 'nonce-{nonce}'; "
		"font-src 'self' https://fonts.gstatic.com https://fonts.googleapis.com https:; "
		f"script-src 'strict-dynamic' 'nonce-{nonce}'; "
		"object-src 'none'; "
		"base-uri 'none'; "
		"img-src 'self' data:; "
		"frame-ancestors 'self'; "
		"media-src *;"
	)
	
	return response


@app.before_request
def preflight():
	if request.method == 'OPTIONS':
		# Let after_request attach the full CORS/security headers
		return Response(status=204)

@app.route('/favicon.ico')
def ico():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'icons/favicon.ico', mimetype='image/vnd.microsoft.icon')



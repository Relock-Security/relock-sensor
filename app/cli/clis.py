import os
import click
import logging
import dotenv

try:
	import werkzeug
except:
	pass
else:
	logging.getLogger("werkzeug").setLevel(logging.ERROR)

from . import cli

logging.basicConfig(level=0)
logging.getLogger('cli.client')

@click.option('--host', is_flag=False, default='127.0.0.1', help=('Host or IP, host:port API.'))
@click.option('--port', is_flag=False, default=80, help=('API port number. Default :80'))
@click.option('--ip', is_flag=False, default='0.0.0.0', help=('IP to assign'))
@click.option('--key', is_flag=False, default='key.pem', help=('Key certyficate'))
@click.option('--crt', is_flag=False, default='cert.pem', help=('Crt file'))
@click.option('--debug', is_flag=True, default=None, help=('Debug mode. Default: True'))
@click.option('--redis_host', is_flag=False, default=str(), help=('Redis host'))
@click.option('--redis_port', is_flag=False, default=str(), help=('Redis port'))
@click.option('--relock_host', is_flag=False, default=str(), help=('Relock service host'))
@click.option('--nginx', is_flag=True, default=False, help=('NGINX mode. Default: False'))
@click.option('--nginx_auth', is_flag=True, default=False, help=('NGINX request_auth. Default: False'))
@cli.command()
def run(host, 
		port,
		ip,
		key,
		crt,
		debug,
		relock_host,
		redis_host,
		redis_port,
		nginx,
		nginx_auth):
	dotenv.load_dotenv()

	if redis_host:
		os.environ['REDIS_HOST'] = redis_host
	if redis_port:
		os.environ['REDIS_PORT'] = redis_port
	if relock_host:
		os.environ['RELOCK_HOST'] = relock_host
	if nginx_auth:
		os.environ['NGINX_AUTH'] = 'True'
	if nginx:
		os.environ['NGINX'] = 'True'

	os.environ['GEVENT_RESOLVER'] = 'ares'
	os.environ['HOST'] = host

	from .. import init_app
	
	app = init_app(host=host, 
				   ip=ip, 
				   port=port,
				   debug=debug)

	app.run(host=ip or host,
			port=port,
			debug=debug)

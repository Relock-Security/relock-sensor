import logging

try:
	from rdbms.src.rvorm import (Logic, register, REGISTRY)
except Exception:
	from rvorm import (Logic, register, REGISTRY)

from contextlib import contextmanager
from flask import current_app as app, session, request

logging = logging.getLogger('models.hostname')

@register
class Hostname(Logic):

	__expire__    = 0
	__interim__   = 0
	__persist__   = 0

	def __init__(self, key:str = str(),
					  *args,
					   pattern:str = 'default',
					   preload:bool = False,
					   auto_commit:bool = True,
					   save_monit:bool = False,
					 **kwargs):
		
		super().__init__(key=key,
					  	*args,
					   	 pattern=pattern,
					   	 preload=preload,
					   	 auto_commit=auto_commit,
					   	 save_monit=save_monit,
					   **kwargs)

	@contextmanager
	@staticmethod
	def __tenancy__():
		if cls := REGISTRY.get('Wildcard'):
			if wildcard := cls(request.host):
				yield hex(wildcard)

	@property
	def name(self):
		return self.key

	@property
	def security(self):
		return True if self.value else False



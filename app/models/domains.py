import logging

try:
	from rdbms.src.rvorm import (Logic, register, REGISTRY)
except Exception:
	from rvorm import (Logic, register, REGISTRY)

from datetime import datetime
from uuid import uuid4
from flask import current_app as app, session, request
from contextlib import contextmanager

@register
class Domains(Logic):

	__expire__    = 0
	__interim__   = 0
	__persist__   = 0

	__kwargs__    = 'id'

	def __init__(self, key:str = None,
					  *args,
					   value:any = None,
					   pattern:str = 'default',
					   preload:bool = False,
					   auto_commit:bool = True,
					 **kwargs):
		if not key:
			key = kwargs.get('id', str()) or str(uuid4())
		if not value:
			value = kwargs.get('organization', str())

		if not int(self) and not self.key and key and value:
			self.key, self.value = (key, value)
			if pattern:
				self.pattern = pattern
			if self.save():
				self.auto_commit = auto_commit
				# logging.trace('%s[%s] has been saved.', self.__class__.__name__, hex(self))
				logging.info('%s[%s] has been saved.', self.__class__.__name__, hex(self))

	@contextmanager
	@staticmethod
	def __tenancy__():
		if cls := REGISTRY.get('Wildcard'):
			if wildcard := cls(request.host):
				yield hex(wildcard)

	@property
	def uuid(self):
		return abs(self)

	def pop(self, key, default=None):
		if id := self.get(key):
			if cls := REGISTRY.get('Wildcard'):
				if object := cls(id):
					object.__destroy__()
				return delattr(self, key)
		return default

	def kill(self):
		if cls := REGISTRY.get('Wildcard'):
			for id in self:
				if object := cls(id):
					object.__destroy__()
		return super().kill()
import logging

try:
	from rdbms.src.rvorm import (Logic, register, REGISTRY)
except Exception:
	from rvorm import (Logic, register, REGISTRY)

from contextlib import contextmanager
from uuid import uuid4
from datetime import datetime
from flask import current_app as app, session, request

from .domains import Domains

@register
class Organization(Logic):

	__expire__    = 0
	__interim__   = 0
	__persist__   = 0

	__kwargs__    = 'id'

	def __init__(self, key:str = None,
					  *args,
					   value:any = list(),
					   pattern:str = 'default',
					   preload:bool = False,
					   auto_commit:bool = True,
					 **kwargs):

		if not key:
			key = kwargs.get('id', str()) or str(uuid4())
		if not value:
			value = kwargs.get('owner', str())

		if not int(self) and not self.key and key and value:
			self.key, self.value = (key, value)
			if pattern:
				self.pattern = pattern
			if self.save():
				self.auto_commit = auto_commit
				if set := Domains(key=hex(self),
								  value=abs(self)):
					setattr(self, 'domains_', hex(set))
				logging.info('%s[%s] has been saved.', self.__class__.__name__, hex(self))

	@contextmanager
	@staticmethod
	def __tenancy__():
		if cls := REGISTRY.get('Wildcard'):
			if wildcard := cls(request.host):
				yield hex(wildcard)

	@property
	def owner(self):
		return getattr(self, '_value', None)

	@owner.setter
	def owner(self, id:int()):
		return setattr(self, '_value', id)

	@property
	def domains(self):
		if not getattr(self, 'domains_', None):
			if set := Domains(key=hex(self),
								  value=abs(self)):
				setattr(self, 'domains_', hex(set))
		if id := getattr(self, 'domains_', int()):
			return Domains(id)
		return dict()

	@domains.deleter
	def domains(self):
		if id := self.domains:
			if domains := Domains(id):
				domains.kill()

	@property
	def hash(self):
		return hex(self)

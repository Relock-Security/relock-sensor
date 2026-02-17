import logging

try:
	from rdbms.src.rvorm import (Logic, register, REGISTRY)
except Exception:
	from rvorm import (Logic, register, REGISTRY)

from contextlib import contextmanager
from datetime import datetime
from uuid import uuid4

from flask import current_app as app, session, request
from flask_login import UserMixin, login_user, logout_user, current_user as worker

from ..plugins.passwd import generate_password_hash, check_password_hash
from .. import login

from .organization import Organization

@register
class Identity(UserMixin, Logic):

	__expire__    = 0
	__interim__   = 0
	__persist__   = 0

	__kwargs__    = 'email'

	def __init__(self, key:str = None,
					  *args,
					   value:any = dict(),
					   pattern:str = 'default',
					   preload:bool = False,
					   auto_commit:bool = True,
					 **kwargs):

		if not key:
			key = kwargs.get('email', str())
		if not value:
			value = kwargs.get('password', str())

		if not self.key and key and value and not int(self):
			self.key, self.value = (key, generate_password_hash(value))
			if pattern:
				self.pattern = pattern
			if self.save():
				self.auto_commit = auto_commit
				if id := kwargs.get('organization', str(uuid4())):
					if organization := Organization(key=id,
													value=hex(self)):
						self.organization = hex(organization)
				# logging.trace('%s[%s] has been saved.', self.__class__.__name__, hex(self))
				logging.info('%s[%s] has been saved.', self.__class__.__name__, hex(self))

	@contextmanager
	@staticmethod
	def __tenancy__():
		if cls := REGISTRY.get('Wildcard'):
			if wildcard := cls(request.host):
				yield hex(wildcard)

	@property
	def organization(self):
		return getattr(self, 'organization_id', int())

	@organization.setter
	def organization(self, id:int()):
		return setattr(self, 'organization_id', id)

	@organization.deleter
	def organization(self):
		if set := Organization(self.organization):
			set.kill()

	def change_password(self, password:str) -> object:
		self.value = generate_password_hash(password)
		return self

	def check_password(self, password:str) -> bool:
		if self.value:
			return check_password_hash(self.value, password)
		return False

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	@property
	def is_strict(self):
		return False

	def get_id(self):
		return hex(self)

	def get_email(self):
		return str(self.email)

	@property
	def email(self):
		return str(self.key)

	@property
	def password(self):
		if self.value:
			return str(self.value)
		return str()

	@password.setter
	def password(self, value:str):
		return str(self.value, value)

	@property
	def verificated(self):
		return getattr(self, 'verificated_', False)

	@verificated.setter
	def verificated(self, value:bool = False):
		setattr(self, 'verificated_', value)

	@staticmethod
	@login.user_loader
	def load(id:int) -> object:
		return Identity(id)

	def login(self, remember:bool=False) -> bool:
		if login_user(self, remember=app.config.get('REMEMBER_ME', remember)):
			return True
		return False

	def logout(self) -> bool:
		if self.is_authenticated and logout_user():
			return self
		return False

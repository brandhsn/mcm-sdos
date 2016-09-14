#!/usr/bin/python
# coding=utf-8

"""
	Project MCM - Micro Content Management
	SDOS - Secure Delete Object Store


	Copyright (C) <2016> Tim Waizenegger, <University of Stuttgart>

	This software may be modified and distributed under the terms
	of the MIT license.  See the LICENSE file for details.


	@author: tim

"""
from mcm.sdos.parallelExecution import Borg
from mcm.sdos.swift import SwiftBackend
from mcm.sdos.core import Frontend


class SwiftPool(Borg):
	"""
		A singleton that manages a pool of swift connections per tenant/user
		only one instance of this class exists at any time -> only one swift connection per user
	"""

	def __init__(self):
		Borg.__init__(self)

		try:
			self.__pool
		except:
			self.__pool = dict()

	def addConn(self, swiftTenant, swiftToken, conn):
		self.__pool[(swiftTenant, swiftToken)] = conn

	def getConn(self, swiftTenant, swiftToken):
		try:
			return self.__pool[(swiftTenant, swiftToken)]
		except:
			sb = SwiftBackend.SwiftBackend(tenant=swiftTenant, token=swiftToken)
			self.addConn(swiftTenant, swiftToken, sb)
			return sb

	def count(self):
		try:
			self.c += 1
		except:
			self.c = 0

		print(self.c)


class FEPool(Borg):
	"""
		A singleton that manages a pool of swift connections per tenant/user
		only one instance of this class exists at any time -> only one swift connection per user
	"""

	def __init__(self):
		Borg.__init__(self)

		try:
			self.__pool
		except:
			self.__pool = dict()

	def addFE(self, container, swiftTenant, swiftToken, fe):
		self.__pool[(container, swiftTenant, swiftToken)] = fe

	def getFE(self, container, swiftTenant, swiftToken):
		try:
			return self.__pool[(container, swiftTenant, swiftToken)]
		except:
			fe = Frontend.SdosFrontend(container, swiftTenant, swiftToken)
			self.addFE(container, swiftTenant, swiftToken, fe)
			return fe

	def count(self):
		try:
			self.c += 1
		except:
			self.c = 0

		print(self.c)

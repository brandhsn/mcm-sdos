#!/usr/bin/python
# coding=utf-8

"""
	Project MCM - Micro Content Management
	SDOS - Secure Delete Object Store


	Copyright (C) <2016> Tim Waizenegger, <University of Stuttgart>

	This software may be modified and distributed under the terms
	of the MIT license.  See the LICENSE file for details.



		WSGI application for the proxy server.
	This service receives requests over a REST API that effectively behaves like a swift server
	 requests are directly forwarded (using a http lib) to swift in order to retrieve objects, containers etc.
	 a swift client lib is then used to issue further (new) requests to swift in order to retrieve the key cascade objects
	 the first response form swift (containing the data object) is then modified (decryption) and passed to the client

"""

import logging
from functools import wraps
from flask import request, Response

from mcm.sdos import configuration
from mcm.sdos.service.Exceptions import HttpError
from mcm.sdos.service import httpBackend, app
from mcm.sdos.core import Frontend
from mcm.sdos.crypto import DataCrypt
from mcm.sdos.util import treeGeometry

log = logging.getLogger()

PSEUDO_OBJECT_PREFIX = "__mcm__/"


##############################################################################
# decorators
##############################################################################
def log_requests(f):
	@wraps(f)
	def logging_wrapper(*args, **kwargs):
		log.debug(
			"<<<{}>>> handles request: {} {} -- HEADERS: {} -- ARGS: {} -- DATA: {}".format(f.__name__, request.method,
			                                                                                request.url,
			                                                                                request.headers,
			                                                                                request.args, request.data))
		return f(*args, **kwargs)

	return logging_wrapper


@app.after_request
def add_mcm_id(response):
	response.headers["MCM-Service-Type"] = "SDOS"
	return response


##############################################################################
# helpers
##############################################################################
def replaceStorageUrl(swiftResponse):
	swiftUrl = swiftResponse['X-Storage-Url']
	if not swiftUrl.startswith(configuration.swift_storage_url.format("")):
		raise HttpError("swift returned wrong storage URL")
	swiftAuthName = swiftUrl[len(configuration.swift_storage_url.format("")):]
	swiftResponse['X-Storage-Url'] = configuration.proxy_storage_url.format(swiftAuthName)


def strip_etag(h):
	h.pop("Etag")
	return h


def add_sdos_flag(h):
	i = dict(h)
	i["X-Object-Meta-MCM-Content"] = DataCrypt.HEADER
	return i


def get_token(request):
	return request.headers["X-Auth-Token"]


def handle_mcm_pseudo_objects(thisAuth, thisContainer, thisObject):
	log.debug("request for MCM pseudo object: {} in container: {}".format(thisObject, thisContainer))
	frontend = Frontend.SdosFrontend(containerName=thisContainer, swiftTenant=thisAuth, swiftToken=get_token(request))
	cascade = frontend.cascade
	if thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_tree_geometry":
		return Response(response=treeGeometry.get_geometry_json(cascade=cascade), status=200, content_type="text/json")
	elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_slot_mapping":
		return Response(response=treeGeometry.get_slot_mapping_json(cascade=cascade), status=200,
		                content_type="text/json")
	elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_slot_mapping_stats":
		return Response(response=treeGeometry.get_slot_mapping_stats_json(cascade=cascade), status=200,
		                content_type="text/json")
	elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_slot_utilization":
		return Response(response=treeGeometry.get_slot_utilization(cascade=cascade), status=200,
		                content_type="text/plain")
	else:
		raise HttpError("unknown pseudo object: {}".format(thisObject))


##############################################################################
# error handler
##############################################################################
@app.errorhandler(Exception)
def handle_invalid_usage(e):
	log.exception("internal error")
	if (HttpError == type(e)):
		return e.to_string(), e.status_code
	return "Exception in the SDOS service; check logs", 400


"""
	Forward the auth request to swift
	replace the given storage url with our own:
	'X-Storage-Url': 'http://192.168.209.204:8080/v1/AUTH_test'
	becomes
	'X-Storage-Url': 'http://localhost:4000/v1/AUTH_test'
	
	this is the first request any client makes; we passed on a auth.token from swift
	which is used in further requests
"""


@app.route("/auth/v1.0", methods=["GET"])
@log_requests
def handle_auth():
	clientHeaders = request.headers
	swiftStatus, swiftHeaders = httpBackend.doAuthGetToken(reqHead=clientHeaders)
	log.debug("swift response: {}".format(swiftHeaders))
	replaceStorageUrl(swiftResponse=swiftHeaders)
	log.debug("proxy response: {}".format(swiftHeaders))
	return Response(response="", status=swiftStatus, headers=swiftHeaders)


##############################################################################
# API functions
##############################################################################

"""
	Account functions
"""


@app.route("/v1/AUTH_<thisAuth>", methods=["HEAD", "POST", "GET", "PUT", "DELETE"])
@log_requests
def handle_account(thisAuth):
	myUrl = configuration.swift_storage_url.format(thisAuth)
	s, h, b = httpBackend.doGenericRequest(method=request.method, reqUrl=myUrl, reqHead=request.headers,
	                                       reqArgs=request.args, reqData=request.data)
	return Response(response=b, status=s, headers=h)


"""
	Container functions
"""


@app.route("/v1/AUTH_<thisAuth>/<thisContainer>", methods=["POST", "GET", "PUT", "DELETE", "HEAD"])
@log_requests
def handle_container(thisAuth, thisContainer):
	myUrl = configuration.swift_storage_url.format(thisAuth)
	myUrl += "/" + thisContainer
	s, h, b = httpBackend.doGenericRequest(method=request.method, reqUrl=myUrl, reqHead=request.headers,
	                                       reqArgs=request.args, reqData=request.data)
	return Response(response=b, status=s, headers=h)


"""
	Object functions
"""


@app.route("/v1/AUTH_<thisAuth>/<thisContainer>/<path:thisObject>", methods=["GET", "HEAD"])
@log_requests
def handle_object_get(thisAuth, thisContainer, thisObject):
	if thisObject.startswith(PSEUDO_OBJECT_PREFIX):
		return handle_mcm_pseudo_objects(thisAuth, thisContainer, thisObject)
	myUrl = configuration.swift_storage_url.format(thisAuth)
	myUrl += "/" + thisContainer + "/" + thisObject
	s, h, b = httpBackend.doGenericRequest(method=request.method, reqUrl=myUrl, reqHead=request.headers,
	                                       reqArgs=request.args, reqData=request.data)
	if (s == 200 and len(b)):
		frontend = Frontend.SdosFrontend(containerName=thisContainer, swiftTenant=thisAuth,
		                                 swiftToken=get_token(request))
		decrypted_b = frontend.decrypt_bytes_object(b, thisObject)
		return Response(response=decrypted_b, status=s, headers=strip_etag(h))
	return Response(response=b, status=s, headers=h)


@app.route("/v1/AUTH_<thisAuth>/<thisContainer>/<path:thisObject>", methods=["DELETE"])
@log_requests
def handle_object_delete(thisAuth, thisContainer, thisObject):
	myUrl = configuration.swift_storage_url.format(thisAuth)
	myUrl += "/" + thisContainer + "/" + thisObject
	s, h, b = httpBackend.doGenericRequest(method=request.method, reqUrl=myUrl, reqHead=request.headers,
	                                       reqArgs=request.args, reqData=request.data)
	if (s == 204):
		frontend = Frontend.SdosFrontend(containerName=thisContainer, swiftTenant=thisAuth,
		                                 swiftToken=get_token(request))
		frontend.deleteObject(thisObject, deleteParentInSwift=False)
		frontend.finish()
		return Response(response=b, status=s, headers=h)
	raise HttpError("deletion failed; swift didn't confirm deletion of the parent object")


@app.route("/v1/AUTH_<thisAuth>/<thisContainer>/<path:thisObject>", methods=["PUT"])
@log_requests
def handle_object_put(thisAuth, thisContainer, thisObject):
	myUrl = configuration.swift_storage_url.format(thisAuth)
	myUrl += "/" + thisContainer + "/" + thisObject

	frontend = Frontend.SdosFrontend(containerName=thisContainer, swiftTenant=thisAuth, swiftToken=get_token(request))
	encrypted_b = frontend.encrypt_bytes_object(o=request.data, name=thisObject)
	frontend.finish()

	s, h, b = httpBackend.doGenericRequest(method=request.method, reqUrl=myUrl, reqHead=add_sdos_flag(request.headers),
	                                       reqArgs=request.args, reqData=encrypted_b)
	return Response(response=b, status=s, headers=strip_etag(h))


@app.route("/v1/AUTH_<thisAuth>/<thisContainer>/<path:thisObject>", methods=["POST"])
@log_requests
def handle_object(thisAuth, thisContainer, thisObject):
	raise HttpError("nothing")

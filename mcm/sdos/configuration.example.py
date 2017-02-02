#!/usr/bin/python
# coding=utf-8

"""
	Project MCM - Micro Content Management
	SDOS - Secure Delete Object Store


	Copyright (C) <2017> Tim Waizenegger, <University of Stuttgart>

	This software may be modified and distributed under the terms
	of the MIT license.  See the LICENSE file for details.

	This is the configuration file for the SDOS core and service components
"""

import logging, os


###############################################################################
"""
	Log level setting
"""
#log_level = logging.CRITICAL
#log_level = logging.ERROR
log_level = logging.WARNING
#log_level = logging.INFO
#log_level = logging.DEBUG #WARNING! this logs sensitive passwords/keys!

"""
################################################################################
Server / runtime config
################################################################################
"""

"""
SDOS runs as a proxy between a swift object store and a client.
swift uses potentially 2 hosts: one for athentication, and one for the store API.
SDOS runs both on the same host/port; only URL-path differs.

Keystone auth (p. 5000) __________ SDOS proxy (p. 3000) __________ Swift client
                              /
Swift store   (p. 8080) _____/
"""

# configure the proxy endpoint that clients connect to

my_endpoint_port = 3000
my_endpoint_host = os.getenv("MY_ENDPOINT_HOST", "127.0.0.1")

my_endpoint_store_url = "http://{}:{}/v1/AUTH_{}".format(my_endpoint_host, my_endpoint_port, "{}")


# configure the swift connection

swift_auth_host = os.getenv("SWIFT_AUTH_HOST", "129.69.209.131")
swift_auth_port = os.getenv("SWIFT_AUTH_PORT", "5000")

swift_auth_url = "http://{}:{}/v2.0/tokens".format(swift_auth_host, swift_auth_port)


swift_store_host = os.getenv("SWIFT_STORE_HOST", "129.69.209.131")
swift_store_port = os.getenv("SWIFT_STORE_PORT", "8080")

swift_store_url = "http://{}:{}/v1/AUTH_{}".format(swift_store_host, swift_store_port, "{}")
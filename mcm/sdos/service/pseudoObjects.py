#!/usr/bin/python
# coding=utf-8

"""
	Project MCM - Micro Content Management
	SDOS - Secure Delete Object Store


	Copyright (C) <2016> Tim Waizenegger, <University of Stuttgart>

	This software may be modified and distributed under the terms
	of the MIT license.  See the LICENSE file for details.



	Handle pseudo objects that allow accessing SDOS/MCM internal data over regular swift object requests

"""

import logging
from flask import Response

from mcm.sdos.service.Exceptions import HttpError
from mcm.sdos.util import treeGeometry

PSEUDO_OBJECT_PREFIX = "__mcm__/"


def dispatch_get_head(sdos_frontend, thisObject):
    logging.debug("GTE/HEAD request for MCM pseudo object: {}".format(thisObject))
    try:
        cascade = sdos_frontend.cascade
        ###############################################################################
        # statistics, visualization
        ###############################################################################
        if thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_used_partitions":
            return Response(response=treeGeometry.get_used_partitions_json(cascade=cascade), status=200,
                            mimetype="application/json")
        elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_partition_mapping":
            return Response(response=treeGeometry.get_partition_mapping_json(cascade=cascade), status=200,
                            mimetype="application/json")
        elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_cascade_stats":
            return Response(response=treeGeometry.get_cascade_stats_json(cascade=cascade), status=200,
                            mimetype="application/json")
        elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_slot_utilization10":
            return Response(response=treeGeometry.get_slot_utilization(cascade=cascade, NUMFIELDS=10), status=200,
                            mimetype="application/json")
        elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_slot_utilization100":
            return Response(response=treeGeometry.get_slot_utilization(cascade=cascade, NUMFIELDS=100), status=200,
                            mimetype="application/json")
        elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_slot_utilization1000":
            return Response(response=treeGeometry.get_slot_utilization(cascade=cascade, NUMFIELDS=1000), status=200,
                            mimetype="application/json")
        elif thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_slot_utilization10000":
            return Response(response=treeGeometry.get_slot_utilization(cascade=cascade, NUMFIELDS=10000), status=200,
                            mimetype="application/json")
        ###############################################################################
        # unknown
        ###############################################################################
        else:
            raise HttpError("unknown pseudo object: {}".format(thisObject))
    except Exception:
        logging.exception("pseudo object API received exception")
        return "check logs", 500


def dispatch_put_post(sdos_frontend, thisObject, data):
    logging.debug("PUT/POST request for MCM pseudo object: {}".format(thisObject))
    try:
        cascade = sdos_frontend.cascade
        ###############################################################################
        # key management actions
        ###############################################################################
        if thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_masterkey_unlock":
            return Response(response=cascade.masterKeySource.unlock_key(), status=200,
                            mimetype="application/json")
        if thisObject[len(PSEUDO_OBJECT_PREFIX):] == "sdos_masterkey_lock":
            return Response(response=cascade.masterKeySource.lock_key(), status=200,
                            mimetype="application/json")
        ###############################################################################
        # unknown
        ###############################################################################
        else:
            raise HttpError("unknown pseudo object: {}".format(thisObject))
    except Exception:
        logging.exception("pseudo object API received exception")
        return "check logs", 500
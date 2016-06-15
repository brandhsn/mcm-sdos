#!/usr/bin/python
# coding=utf-8

"""
	Project MCM - Micro Content Management
	SDOS - Secure Delete Object Store


	Copyright (C) <2016> Tim Waizenegger, <University of Stuttgart>

	This software may be modified and distributed under the terms
	of the MIT license.  See the LICENSE file for details.
"""

import logging
import sys
import io
import time
import statistics
from mcm.sdos.core import Frontend
from mcm.sdos import configuration

logging.basicConfig(level=configuration.log_level, format=configuration.log_format)
log = logging.getLogger()


###############################################################################
###############################################################################

def calculateTimeDeltas(absoluteTimes):
	a = []
	for i in range(1, len(absoluteTimes)):
		a.append(absoluteTimes[i] - absoluteTimes[i - 1])
	return a


def loadTestData(path):
	# log.info('loading test data from: %s' % (path))
	f = open(path, mode='rb')
	o = io.BytesIO(f.read())
	f.close()
	return o


def saveTestData(o, path):
	f = open(path, mode='wb')
	f.write(o.getvalue())
	f.close()
	o.__del__()


def runPutTest(testDataPath, testDataRangeStart, testDataRangeEnd, f):
	log.debug('running put tests...')
	timeStart = time.perf_counter()
	times = [time.perf_counter()]
	for i in range(testDataRangeStart, testDataRangeEnd):
		thisPath = '%s/%i' % (testDataPath, i)
		o = loadTestData(thisPath)

		f.putObject(o, str(i))

		times.append(time.perf_counter())

	timeEnd = time.perf_counter()
	log.warning('RESULT (PUT): total test runtime: %s seconds, mean per object: %s' % (
		timeEnd - timeStart, ((timeEnd - timeStart) / testDataRangeEnd)))
	log.warning('RESULT (PUT): median result: %s ' % statistics.median(calculateTimeDeltas(times)))
	log.warning('RESULT (PUT): standard deviation result: %s ' % statistics.stdev(calculateTimeDeltas(times)))
	log.warning('RESULT (PUT): mean result: %s ' % statistics.mean(calculateTimeDeltas(times)))


# log.warning('RESULT (PUT): individual times: %s ' % (calculateTimeDeltas(times)))

def runGetTest(testDataPath, testDataRangeStart, testDataRangeEnd, f):
	log.debug('running get tests...')
	timeStart = time.perf_counter()
	times = [time.perf_counter()]
	for i in range(testDataRangeStart, testDataRangeEnd):
		thisPath = '%s/%i' % (testDataPath, i)

		o = f.getObject(str(i))
		saveTestData(o, thisPath)

		times.append(time.perf_counter())

	timeEnd = time.perf_counter()
	log.warning('RESULT (GET): total test runtime: %s seconds, mean per object: %s' % (
		timeEnd - timeStart, ((timeEnd - timeStart) / testDataRangeEnd)))
	log.warning('RESULT (GET): median result: %s ' % statistics.median(calculateTimeDeltas(times)))
	log.warning('RESULT (GET): standard deviation result: %s ' % statistics.stdev(calculateTimeDeltas(times)))
	log.warning('RESULT (GET): mean result: %s ' % statistics.mean(calculateTimeDeltas(times)))


# log.warning('RESULT (GET): individual times: %s ' % (calculateTimeDeltas(times)))

def runDeleteTest(testDataRangeStart, testDataRangeEnd, f):
	log.debug('running delete tests...')
	timeStart = time.perf_counter()
	times = [time.perf_counter()]
	for i in range(testDataRangeStart, testDataRangeEnd):
		f.deleteObject(str(i))

		times.append(time.perf_counter())

	timeEnd = time.perf_counter()
	log.warning('RESULT (DELETE): total test runtime: %s seconds, mean per object: %s' % (
		timeEnd - timeStart, ((timeEnd - timeStart) / testDataRangeEnd)))
	log.warning('RESULT (DELETE): median result: %s ' % statistics.median(calculateTimeDeltas(times)))
	log.warning('RESULT (DELETE): standard deviation result: %s ' % statistics.stdev(calculateTimeDeltas(times)))
	log.warning('RESULT (DELETE): mean result: %s ' % statistics.mean(calculateTimeDeltas(times)))


# log.warning('RESULT (DELETE): individual times: %s ' % (calculateTimeDeltas(times)))



###############################################################################
###############################################################################

if __name__ == '__main__':
	log.debug('perftest start')
	log.debug(sys.version)
	log.debug(sys.flags)
	# frontend = Frontend.DirectFrontend(containerName='sdosTest1', swiftUser = 'test:tester', swiftKey = 'testing')
	# frontend = Frontend.CryptoFrontend(containerName='sdosTest1', swiftUser = 'test:tester', swiftKey = 'testing')
	frontend = Frontend.SdosFrontend(containerName='sdosTest2', swiftUser = 'test:tester', swiftKey = 'testing')

	#runPutTest('/home/tim/sdos-measure/testdata/1kB', 0, 10, frontend)
	runGetTest('/home/tim/sdos-measure/testdata/result', 0, 10, frontend)
	# runGetTest('/dev/shm/res', 0, 5, frontend)
	#runDeleteTest(110,150, frontend)
	# runGetTest('/home/tim/sdos-measure/testdata/result_100kB', 1, 3, frontend)
	# runGetTest('/dev/shm/result_1kB', 1000, frontend)

	frontend.finish()

#!/usr/bin/python

import os
import time
import pyProcenet

def spend_time(s):
	start_time = time.time()
	end_time = start_time

	while end_time - start_time < s:
		for i in xrange(1000000):
			pass
		end_time = time.time()

def test1():
	""" Simpe test """
	
	pid = os.getpid()
	cpid = os.fork()

	if cpid == 0:
		# Run for5 seconds
		pyProcenet.invite(pid, None)
		spend_time(5)
		return

	start_time = time.time()
	pyProcenet.invite(pid, None)
	pyProcenet.invite(cpid, None)
	time.sleep(4)
	end_time = time.time()
	os.wait()

	print(end_time - start_time)
	assert end_time - start_time > 3
	assert end_time - start_time < 5

if __name__ == "__main__":
	test1()

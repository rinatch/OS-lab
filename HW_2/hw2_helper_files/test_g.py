#!/usr/bin/python

import os
import time
import pyProcenet

def spend_more_time(s):
	start_time = time.time()
	end_time = start_time	
	while end_time - start_time < s:
		for i in xrange(1000000):
			pass
		end_time = time.time()


def spend_time(s, pid):
	flag = 0
	start_time = time.time()
	end_time = start_time
		
	while end_time - start_time < s:
		for i in xrange(1000000):
			pass
			
			if flag == 0:
				pyProcenet.invite(pid, None)
				spend_more_time(3)
				pyProcenet.respond(pid, 0)
				flag = 1
		end_time = time.time()

def test1():
	""" Simpe test """
	
	pid = os.getpid()
	cpid = os.fork()
	
	if cpid == 0:
		# Run for5 seconds
		spend_time(5, pid)
		return

	start_time = time.time()
	pyProcenet.invite(cpid, None)
	end_time = time.time()
	os.wait()
	final_time = time.time()

	#assert 2.5 < end_time - start_time < 3.5
	assert final_time - start_time > 4.5
	assert final_time - start_time < 6

if __name__ == "__main__":
	test1()

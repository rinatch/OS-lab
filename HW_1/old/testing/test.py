#!/usr/bin/python

import os
import pyProcenet

def test1():
	"""simple test to invoke the syscalls with no error."""
	
	pid = os.getpid()

	# Invite
	pyProcenet.invite(pid, "Hello me, meet the real me, and my misfit's way of life")
	
	# Fetch our invitation
	invitations, remaining = pyProcenet.invitations(1)
	assert (remaining == 0) # No more invitations to read
	assert (invitations[0] == pid)
	print("Invitation message:", invitations[0][1])
	
	# Accept
	pyProcenet.respond(pid, 1)

	# Get our friends
	friends = pyProcenet.info(pid)
	assert (len(friends) == 1) # We expect one friend
	if friends[0][1]:
		print("Our friend", friends[0][0], "is alive")
	else:
		print("Our friend", friends[0][0], "is dead!")

if __name__ == "__main__":
	test1()

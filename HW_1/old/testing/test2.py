#!/usr/bin/python

import os
import pyProcenet

def test1():
    """simple test to invoke the syscalls with no error."""
    parent_pid = os.getpid()
    pid = os.fork()
    if pid > 0:
        #parent
        #Invite
        """"
        # Fetch our invitation
        status = os.wait()
        #son should be dead!
        invitations, remaining = pyProcenet.invitations(1)
        assert (remaining == 0) # No more invitations to read
        
        #assert (invitations[0][0] == pid)
        print("Invitation message:", invitations[0][1])
        """
        # Accept
        print("child pid was:", status[0])
        pyProcenet.respond(status[0], 1)
        # Get our friends
        """"
        friends = pyProcenet.info(parent_pid)
        assert (len(friends) == 1) # We expect one friend
        if friends[0][1]:
            print("Our friend", friends[0][0], "is alive")
        else:
            print("Our friend", friends[0][0], "is dead!")
    """
    else:
        #child
        pyProcenet.invite(parent_pid, "Hello papa, meet your son")
        
if __name__ == "__main__":
	test1()

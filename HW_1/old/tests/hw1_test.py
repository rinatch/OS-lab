#!/usr/bin/python

from __future__ import division
from hwgrader.test_utils import memTrack
from hwgrader.test_utils import *
from hwgrader.utils import ParTextTestRunner, ParTestCase
import unittest
import shutil
import sys
import os
import errno
import pickle

EXTENSION_FILES = ('setup.py', 'py_procenet.c')
EXTENSION_LIB = 'pyProcenet'
HEADER_FILE = 'procenet_api.h'
TEMP_FOLDER = 'temp'
EXT_SUCCESSFUL = True
DEFAULT_MESSAGE = "Hi! Please be my friend"
MAX_FRIENDS = 32

class hw_test(ParTestCase):
    """Basic test"""

    def get_missing_pid(self):
        pid_list = os.popen('cd /proc; ls -d [1-9]* | sort -n').read().strip().split('\n')
        pid_list = [ int(p) for p in pid_list ]
        for missing_pid in range(1, 16000):
            if missing_pid not in pid_list:
                break
        return missing_pid

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_header(self):
        """Verify that the header file compiled successfuly."""

        self.assert_(EXT_SUCCESSFUL, 'Failed compilation of %s.' % HEADER_FILE)
        
    def test_invite1(self):
        """ Test invalid pid """
        self.errnoCheck(
            cmd=pyProcenet.invite,
            args=(0, "hello"),
            expected_errno=errno.EINVAL,
            msg='invite should fail with invalid pid')
        
    def test_invite2(self):
        """ Test missing pid """
        self.errnoCheck(
            cmd=pyProcenet.invite,
            args=(self.get_missing_pid(), "hello"),
            expected_errno=errno.ESRCH,
            msg='invite should fail with missing pid')

    def test_invite3(self):
        """ Test valid invitation"""
        pid = os.getpid()
        pyProcenet.invite(pid, None)
        
    def test_respond1(self):
        """ Test no invitation """
        self.errnoCheck(
            cmd=pyProcenet.respond,
            args=(1, 1),
            expected_errno=errno.ESRCH,
            msg='respond should fail when no invitation exists')

    def test_respond2(self):
        """ Test bad response """
        pid = os.getpid()
        pyProcenet.invite(pid, None)
        self.errnoCheck(
            cmd=pyProcenet.respond,
            args=(pid, 2352),
            expected_errno=errno.EINVAL,
            msg='respond should fail on invalid response')

    def test_respond3(self):
        """ Test valid response """
        pid = os.getpid()
        pyProcenet.invite(pid, None)
        pyProcenet.respond(pid, 0)

    def test_invitations1(self):
        """ Test on empty invitations list """
        invitations, remaining = pyProcenet.invitations(2)

        assert invitations == ()
        assert remaining == 0

    def test_friends1(self):
        """ Test info on ourselves """
        pid = os.getpid()
        friends = pyProcenet.info(pid)

        assert friends == ()

    def test_friends2(self):
        """ Test info on another process """
        friends = pyProcenet.info(1)

        assert friends == ()

    def test_friends3(self):
        """ Test info on another process that doesn't exist"""
        self.errnoCheck(
            cmd=pyProcenet.info,
            args=(self.get_missing_pid(),),
            expected_errno=errno.ESRCH,
            msg='info should fail on non existing process')

    def test_invite_default_msg(self):
        """ Test inviting with default message"""
        pid = os.getpid()
        fork = tfork2()
        if fork.isChild:
	    pyProcenet.invite(fork.ppid, None)
            fork.exit()
        fork.wait()

        invitations, remaining = pyProcenet.invitations(1)
        assert (len(invitations) == 1)
        assert (invitations[0][0] == fork.cpid)
        assert (invitations[0][1] == DEFAULT_MESSAGE)
        assert (remaining == 0)
        
    def test_invite_custom_msg(self):
        """ Test inviting with non-default message"""
        pid = os.getpid()
        fork = tfork2()
        message =  "Hello! My name is Elder Price."
        if fork.isChild:
	    pyProcenet.invite(fork.ppid, message)
            fork.exit()
        fork.wait()

        invitations, remaining = pyProcenet.invitations(1)
        assert (len(invitations) == 1)
        assert (invitations[0][0] == fork.cpid)
        assert (invitations[0][1] == message)
        assert (remaining == 0)
        
    def test_invitation_exists(self):
        """ Test inviting when invitation already exists"""
        pid = os.getpid()
        fork = tfork2()
        if fork.isChild:
	    pyProcenet.invite(fork.ppid, "Hello! My name is Elder Price.")
	    pyProcenet.invite(fork.ppid, "Hello! My name is Elder Price.")
            fork.exit()
        fork.release()
        fork.wait()

        _, remaining = pyProcenet.invitations(0)
        assert (remaining == 1)

    def test_inviting_friend(self):
        """ Test inviting an existing friend """
        pid = os.getpid()
        pyProcenet.invite(pid, None)
        pyProcenet.respond(pid, 1)
        self.errnoCheck(
            cmd=pyProcenet.invite,
            args=(pid, None),
            expected_errno=errno.EEXIST,
            msg='inviting a friend should fail')

    def test_reject(self):
        """ Test reject response """
        pid = os.getpid()
        pyProcenet.invite(pid, None)
        pyProcenet.respond(pid, 0)

        _, remaining = pyProcenet.invitations(0)
        friends = pyProcenet.info(pid)
        
        assert (remaining == 0)
        assert (len(friends) == 0)

    def test_accept(self):
        """ Test accept response """
        fork = tfork2()
        if fork.isChild:
            pyProcenet.invite(fork.ppid, None)
            fork.release()
            fork.sync()
            fork.exit()
        fork.sync()
        pyProcenet.respond(fork.cpid, 1)

        _, remaining = pyProcenet.invitations(0)
        friends_parent = pyProcenet.info(fork.ppid)
        friends_child = pyProcenet.info(fork.cpid)
        fork.release()
        fork.wait()

        assert (remaining == 0)
        assert (len(friends_parent) == 1)
        assert (len(friends_child) == 1)
        assert (friends_parent[0] == (fork.cpid, 1))
        assert (friends_child[0] == (fork.ppid, 1))

    def test_accept_deceased(self):
        """ Test accept from deceased process"""
        fork = tfork2()
        if fork.isChild:
            pyProcenet.invite(fork.ppid, None)
            fork.exit()
        fork.wait()
        pyProcenet.respond(fork.cpid, 1)

        _, remaining = pyProcenet.invitations(0)
        friends = pyProcenet.info(fork.ppid)

        assert (remaining == 0)
        assert (len(friends) == 1)
        assert (friends[0] == (fork.cpid, 0))

    def test_too_many_friends(self):
        """ Test reaching end of friends list """
        # Accept MAX_FRIENDS friends
        for i in range(MAX_FRIENDS):
            fork = tfork2()
            if fork.isChild:
                pyProcenet.invite(fork.ppid, None)
                fork.exit()
            fork.wait()
            pyProcenet.respond(fork.cpid, 1)

        # Try to accept one more
        pid = os.getpid()
        pyProcenet.invite(pid, None)
        self.errnoCheck(
            cmd=pyProcenet.respond,
            args=(pid, 1),
            expected_errno=errno.ENOSPC,
            msg='respond should fail on full friends list')

    def test_dying_friend(self):
        """ Test friend dying and becoming deceased """
        fork = tfork2()
        if fork.isChild:
            pyProcenet.invite(fork.ppid, None)
            fork.release()
            fork.sync()
            fork.exit()
        fork.sync()
        pyProcenet.respond(fork.cpid, 1)
        friends_alive = pyProcenet.info(fork.ppid)
        fork.release()
        fork.wait()

        friends_dead = pyProcenet.info(fork.ppid)

        assert (len(friends_alive) == 1)
        assert (len(friends_dead) == 1)
        assert (friends_alive[0] == (fork.cpid, 1))
        assert (friends_dead[0] == (fork.cpid, 0))

    def test_fork(self):
        """ Test friend and invitation list emptying on fork """
        fork = tfork2()
        if fork.isChild:
            pyProcenet.invite(fork.ppid, None)
            fork.exit()
        fork.wait()
        pyProcenet.invite(fork.ppid, None)
        pyProcenet.respond(fork.cpid, 1)

        fork = tfork2()
        if fork.isChild:
            friends = pyProcenet.info(fork.cpid)
            _, remaining = pyProcenet.invitations(0)

            assert (len(friends) == 0)
            assert (remaining == 0)
            fork.exit()
        fork.wait()

    def test_memory(self):
        """ Test memory is properly freed"""
        mm_track = memTrack()
        mm_track.start_track()
        message = "Hello. Is it me you're looking for?"
        try:
            fork = tfork2()
            if fork.isChild:
                fork.sync()
                pyProcenet.invite(fork.cpid, None)
                pyProcenet.respond(fork.cpid, 1)
                fork.exit()
            pyProcenet.invite(fork.cpid, message)
            fork.wait()
        finally:
            mm_track.close()


def compile_extension(test_folder, submission_folder):
            
    global EXT_SUCCESSFUL
    
    #
    # Prepare a temporary folder with all necessary files.
    #
    temp_folder = os.path.join(test_folder, TEMP_FOLDER)
    os.chdir(test_folder)
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
    os.mkdir(temp_folder)
    
    shutil.copy(os.path.join(submission_folder, HEADER_FILE), temp_folder)
    for file in EXTENSION_FILES:
        shutil.copy(os.path.join(test_folder, file), temp_folder)
    
    #
    # Compile the extension module and import it into the modules namespace
    # Note:
    # I am saving the sys.argv because the run_setup script overwrites them
    # due to a bug
    #
    os.chdir(temp_folder)
    from distutils.core import run_setup
    save_argv = list(sys.argv)
    run_setup('setup.py', script_args=['build_ext', '-b', temp_folder])
    sys.argv = save_argv
    
    if os.path.exists(os.path.join(temp_folder, EXTENSION_LIB + '.so')):
        EXT_SUCCESSFUL = True
        #sys.path.append(temp_folder)
    else:
        EXT_SUCCESSFUL = False
        #sys.path.append(test_folder)

    #
    # Note,
    # In any case I use my extension.
    #
    sys.path.append(test_folder)
    os.chdir(test_folder)

    globals().update({EXTENSION_LIB: __import__(EXTENSION_LIB)})
    del sys.path[-1]


def suite(**args):
    
    #
    # First, compile the extension
    #
    test_folder = os.path.split(args['test_path'])[0]
    submission_folder = args['submission_path']
    compile_extension(test_folder, submission_folder)

    #
    # Return the test suite
    #
    return unittest.makeSuite(hw_test, prefix='test')


if __name__ == "__main__":


    script_path = os.path.abspath(sys.argv[0])
    test_folder = os.path.split(script_path)[0]
    submission_folder = test_folder
    
    #
    # Compile the extension
    #
    compile_extension(test_folder, submission_folder)

    #
    # Run the tests
    #
    unittest.main(testRunner=ParTextTestRunner())



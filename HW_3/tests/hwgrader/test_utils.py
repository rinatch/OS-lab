#!/usr/bin/python

from __future__ import division, generators
from hwgrader.utils import TestError
from hwgrader.module_utils import _IOW
from hwgrader import MMLOG_DEVICE_PATH, MMLOG_MODULE_LOAD, MMLOG_MODULE_UNLOAD
import fcntl
import pickle
import shutil
import time
import errno
import sys
import os
import re

__all__ = [
    'KERN_IDLE',
    'KERN_EMERG',
    'KERN_ALERT',
    'KERN_CRIT',
    'KERN_ERR',
    'KERN_WARNING',
    'KERN_NOTICE',
    'KERN_INFO',
    'KERN_DEBUG',
    'ESRCH',
    'ENOMEM',
    'EFAULT',
    'EINVAL',
    'LOG_BUF_LEN',
    'stubTestcase',
    'memTrack',
    'tfork',
    'tfork2',
    'enumerate',
    'count'
    ]


#
# Kernel printk log levels.
#
KERN_IDLE =   -1
KERN_EMERG =   0 # system is unusable
KERN_ALERT =   1 # action must be taken immediately
KERN_CRIT =    2 # critical conditions
KERN_ERR =     3 # error conditions
KERN_WARNING = 4 # warning conditions
KERN_NOTICE =  5 # normal but significant condition
KERN_INFO =    6 # informational
KERN_DEBUG =   7 # debug-level messages

#
# Error codes
#
ESRCH =        3 # No such process
ENOMEM =      12 # Out of memory
EFAULT =      14 # Bad address
EINVAL =      22 # Invalid argument

#
# The size of the ring buffer is increased (modified 'printk.c')
# Therefore we need to read more using the dmesg command.
#
LOG_BUF_LEN = 1048576

TEMP_FOLDER = 'temp'


class stubTestcase(object):
    """Class that enbles running the memTrack tests outside a unittest"""
    
    def fail(self, msg=None):
        """Fail immediately, with the given message."""
        raise Exception, msg
    
    def assert_(self, expr, msg=None):
        """Fail the test unless the expression is true."""
        
        if not expr: raise Exception, msg
        
    
class memTrack(object):
    """Track kernel memory allocation and release."""
    
    def __init__(self):
        #
        # Calculate the ioctl cmd number
        #
        MMLOG_MAGIC = 'r'
        self.MMLOG_SET_LOG_LEVEL = _IOW(MMLOG_MAGIC, 0, 'int')
        
        #
        # Just in case:
        #
        try:
            os.system(MMLOG_MODULE_UNLOAD)
        except:
            pass

        out = os.popen('dmesg -c -s %d' % LOG_BUF_LEN)
        out.close()
    
    def open(self):
        #
        # Load the module
        #
        if os.system(MMLOG_MODULE_LOAD):
            raise Exception('Failed loading the module\n') 

        self.f_dev = os.open(MMLOG_DEVICE_PATH, os.O_RDWR)
        
    def __del__(self):
        if self.f_dev:
            self.close()
        
    def close(self):
        if self.f_dev:
            fcntl.ioctl(self.f_dev, self.MMLOG_SET_LOG_LEVEL, KERN_IDLE)
            os.close(self.f_dev)
            self.f_dev = None
        
            try:
                os.system(MMLOG_MODULE_UNLOAD)
            except:
                pass
        
    def track_func(self, func, args):
        """Track KMALLOC/KFREE calls during the exection of func with args"""

        try:
            self.start_track()
            ret = func(*args)
        finally:
            self.end_track()
        
        return ret

    def start_track(self):
        """Start tracking KMALLOC/KFREE calls"""
        
        self.open()
        fcntl.ioctl(self.f_dev, self.MMLOG_SET_LOG_LEVEL, KERN_ALERT)

    def end_track(self):
        """Stop tracking KMALLOC/KFREE calls"""

        fcntl.ioctl(self.f_dev, self.MMLOG_SET_LOG_LEVEL, KERN_IDLE)
        self.close()

    def validate(self, tracked_pids, test_case=stubTestcase, debug=False):
        """Validate (previous) KMALLOC/KFREE calls of a set of tasks (pids)"""
        
        out = os.popen('dmesg -c -s %d' % LOG_BUF_LEN)
        dmesg_lines = out.readlines()
        out.close()
        
        allocations = []
        memory_allocated = False
        
        if debug:
            f = open('mm_debug.txt', 'w+')
            f.write('All KMALLOC/KFREE messages:\n\n')
            f.write(''.join(dmesg_lines))
            f.write('\nTracked pids: %s\nOnly relevant KMALLOC/KFREE messages:\n' % repr(tracked_pids))
            
            for line in dmesg_lines:
                re_result = re.search(r'.*?(KMALLOC|KFREE) (\d*) (\w*)', line)
                if not re_result:
                    continue
                
                action = re_result.group(1)
                pid = int(re_result.group(2))
                address = re_result.group(3)
                
                if pid not in tracked_pids:
                    continue
                
                f.write(line)

            f.write('\nProcessing KMALLOC/KFREE messages:\n')
        
        try:
            for line in dmesg_lines:
                re_result = re.search(r'.*?(KMALLOC|KFREE) (\d*) (\w*)', line)
                if not re_result:
                    continue
                
                action = re_result.group(1)
                pid = int(re_result.group(2))
                address = re_result.group(3)
                
                if pid not in tracked_pids:
                    continue
    
                if debug:
                    f.write(line)
                    
                if action == 'KMALLOC':
                    memory_allocated = True
                    if address in allocations:
                        test_case.fail('Same address, %s, allocated twice without release.' % address)
                        break
                    allocations.append(address)
                    
                if action == 'KFREE':
                    if address not in allocations:
                        test_case.fail('Freeing a non allocated address, %s.' % address)
                        break
                    allocations.remove(address)
            else:
                test_case.assert_(memory_allocated, 'No memory allocated during execution.')                
                test_case.assert_(not allocations, 'Failed to free some of the allocated memory, left %d:\n%s' % (len(allocations), '\n'.join(allocations)))
        finally:
            if debug:
                f.close()

                
class tfork(object):
    """A convenient fork"""

    def __init__(self):
        """Create a fork"""

        self._ppid = os.getpid()
        self._cpid = os.fork()
        self._inchild = self._cpid == 0
        self._fork_time = time.time()
        self._exit_time = 0
        self._exit_code = 0
        
        if self._inchild:
            self._cpid = os.getpid()
            
    def _isChild(self):

        return self._inchild
    isChild = property(fget=_isChild)    
        
    def _get_cpid(self):
        
        return self._cpid
    cpid = property(fget=_get_cpid)    
    
    def _get_ppid(self):
        
        return self._ppid
    ppid = property(fget=_get_ppid)    

    def exit(self, status=0):

        if not self._inchild:
            raise TestError('Requested exit() in parent')

        os._exit(status)
        
    def wait(self):

        if self._inchild:
            raise TestError('Requested wait() in child')

        pid, exit_code = os.wait()
        
        self._exit_time = time.time()
        self._exit_code = exit_code
        
    def _get_fork_time(self):
        
        return self._fork_time
    fork_time = property(fget=_get_fork_time)    

    def _get_exit_time(self):
        
        if self._inchild:
            raise TestError('Exit time is available only in parent')

        return self._exit_time
    exit_time = property(fget=_get_exit_time)    
    
    def _get_exit_code(self):
        
        if self._inchild:
            raise TestError('Exit code is available only in parent')

        return self._exit_code
    exit_code = property(fget=_get_exit_code)    


def safe_close(fd):
    
    try:
        os.close(fd)
    except:
        pass


class tfork2(tfork):
    """A convenient fork with two way pipe communication"""
    RELEASE_MSG = 'release'
    
    def __init__(self):
        """Create a fork"""

        #
        # One set of pipes is used for synchronization
        # The general pipe is used for general communication of the test
        #
        self._pr_parent, self._pw_child = os.pipe()
        self._pr_child, self._pw_parent = os.pipe()
        self._general_pr_parent, self._general_pw_child = os.pipe()
        self._general_pr_child, self._general_pw_parent = os.pipe()

        super(tfork2, self).__init__()

        self.close_other()
        
    def close_self(self):
        if self._inchild:
            safe_close(self._pr_child)
            safe_close(self._pw_child)
            safe_close(self._general_pr_child)
            safe_close(self._general_pw_child)
        else:
            safe_close(self._pr_parent)
            safe_close(self._pw_parent)
            safe_close(self._general_pr_parent)
            safe_close(self._general_pw_parent)
        
    def close_other(self):
        if self._inchild:
            safe_close(self._pr_parent)
            safe_close(self._pw_parent)
            safe_close(self._general_pr_parent)
            safe_close(self._general_pw_parent)
        else:
            safe_close(self._pr_child)
            safe_close(self._pw_child)
            safe_close(self._general_pr_child)
            safe_close(self._general_pw_child)
        
    def exit(self, status=0):

        if not self._inchild:
            raise TestError('Requested exit() in parent')

        self.close_self()
        
        os._exit(status)
        
    def wait(self, self_close=True):

        if self._inchild:
            raise TestError('Requested wait() in child')

        if self_close:
            self.close_self()
            
        pid, exit_code = os.wait()
        
        self._exit_time = time.time()
        self._exit_code = exit_code
        
    def sync(self):
        """Wait for the other side of the fork to release this side"""

        if self._inchild:
            os.read(self._pr_child, len(self.RELEASE_MSG))
        else:
            os.read(self._pr_parent, len(self.RELEASE_MSG))
            
    def release(self):
        """Release for the other side of the fork that is syncing this side"""

        if self._inchild:
            os.write(self._pw_child, self.RELEASE_MSG)
        else:
            os.write(self._pw_parent, self.RELEASE_MSG)

    def send(self, message):
        """Send from this side of the pipe to the other side"""

        if self._inchild:
            os.write(self._general_pw_child, message)
        else:
            os.write(self._general_pw_parent, message)
            
    def receive(self, message_length=100):
        """Receive a message sent from the other side of the pipe to the this side"""

        if self._inchild:
            return os.read(self._general_pr_child, message_length)
        else:
            return os.read(self._general_pr_parent, message_length)

    def send2(self, message):
        """Send from this side of the pipe to the other side, synchronously (the function returns only when the other party signaled receive)"""

        self.send(message)
        self.sync(message)
            
    def receive2(self, message_length=100):
        """Receive a message sent from the other side of the pipe to the this side, synchronously (let the other party know that recieved)"""

        self.receive(message)
        self.release(message)

    def _wpipe(self):
        """Return the correct write side of the general pipe"""

        if self._inchild:
            return self._general_pw_child
        else:
            return self._general_pw_parent
            
    def _rpipe(self):
        """Return the correct read side of the general pipe"""

        if self._inchild:
            return self._general_pr_child
        else:
            return self._general_pr_parent
            
    wpipe = property(fget=_wpipe)    
    rpipe = property(fget=_rpipe)    

    def pickle_dump(self, data):
        """Dump data through the pipe. The data is sent using pickle binary format."""
        
        os.write(self.wpipe, pickle.dumps(data, bin=True))
        
    def pickle_load(self):
        """Load data from the pipe. The data is sent using pickle binary format."""
        
        #
        # I am wrapping the file descriptor because this way pickle
        # returns on each data send separately (allowing for sending
        # multiple data before reading).
        # I close the file descriptor or else for some reason just
        # closing the write side of the pipe doesn't raise an EOF
        # in the read side.
        #
        if not hasattr(self, '_rf'):
            self._rf = os.fdopen(os.dup(self.rpipe), 'r')
            
        data = pickle.load(self._rf)
        
        return data


def compile_extension(
    test_folder,
    submission_folder,
    _globals
    ):
    
    #
    # Prepare a temporary folder with all necessary files.
    
    import tempfile
    temp_folder = tempfile.mktemp()
    os.mkdir(temp_folder)

    shutil.copy(os.path.join(submission_folder, _globals['__header_file__']), temp_folder)
    for file in _globals['__extension_files__']:
        shutil.copy(os.path.join(test_folder, file), temp_folder)
    shutil.copy(os.path.abspath(sys.argv[0]), temp_folder)
    
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
    
    if os.path.exists(os.path.join(temp_folder, _globals['__module_name__']+'.so')):
        compile_success = True
        sys.path.append(temp_folder)
    else:
        compile_success = False
        sys.path.append(test_folder)

    _globals.update({_globals['__module_name__']: __import__(_globals['__module_name__'])})
    del sys.path[-1]

    return compile_success


class ErrnoError(Exception):
    def __init__(self, e, msg):
        self.errno = e.errno
        self.msg = msg
        
    def __str__(self):
        return '%s %s' % (errno.errorcode[self.errno], self.msg)


def enumerate(collection):
    'Generates an indexed series:  (0,coll[0]), (1,coll[1]) ...'     
    i = 0
    it = iter(collection)
    while 1:
        yield (i, it.next())
        i += 1


COUNT_FILE_NAME = os.path.join(os.path.expanduser('~'), 'last_count.txt')

def count(start=0, step=1, persistent=False):
    # count(10) --> 10 11 12 13 14 ...
    # count(2.5, 0.5) -> 2.5 3.0 3.5 ...
    
    if persistent:
        if os.path.exists(COUNT_FILE_NAME):
            f = open(COUNT_FILE_NAME, mode='r')
            start = int(f.read().strip()) + 1
            f.close()
    
    n = start
    
    while True:
        if persistent:
            f = open(COUNT_FILE_NAME, mode='w')            
            f.write('%d' % n)
            f.close()
        
        yield n
        n += step


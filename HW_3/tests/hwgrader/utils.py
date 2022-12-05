#!/usr/bin/python

from __future__ import division
from grader_globals import *
import sys
import os
import unittest
import tempfile
import pickle
import signal
import time
import sys
import traceback
import select
import string
import types
import re
import errno
import fcntl
import shutil
import fileinput
import warnings
import ConfigParser
import glob

__all__ = [
    'prompt_with_timeout',
    'import_path',
    'submission_paths',
    'get_submitters',
    'add_grade',
    'add_stats',
    'unzip_submission',
    'ParTextTestRunner',
    'ParTestCase',
    'TestError',
    'TestStatus',
    'RebootableTestSuite',
    'set_grub',
    'init_bash',
    'init_sysctl',
    'init_autologin',
    'init_grader',
    'end_bash',
    'end_sysctl',
    'end_autologin',
    'end_grader',
    'next_submission'
    ]

#
# Prepare a list of signal code/name
#
SIGNALS_DICT = {}
for name in dir(signal):
    if name[:3] == 'SIG' and name[:4] != 'SIG_':
        SIGNALS_DICT[getattr(signal, name)] = name

        
class TimeoutException(Exception):
    """A timeout has occurred."""
    pass


class TestError(Exception):
    """An error that occurs during the execution of a test."""
    pass


def timeout_handler(signum, frame):
    raise TimeoutException('Timeout occured')


def test_timeout_handler(signum, frame):
    raise TimeoutException('Timeout occured before test ended')


def getch():
    import tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch
    
    
def prompt_with_timeout(prompt='Press any key to abort operation', timeout=5):
    """main"""
    
    #
    # Set the signal handler and a 5-second timeout alarm
    #
    old_signal_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    ch = None
    try:
        print prompt + ' (timeout in %d seconds)' % timeout
        ch = getch()
    except TimeoutException:
        pass
    
    #
    # Restore existing SIGALRM handler and halt the alarm
    #
    signal.signal(signal.SIGALRM, old_signal_handler)
    signal.alarm(0)

    return ch


def import_path(fullpath):
    """ 
    Import a file with full path specification. Allows one to
    import from anywhere, something __import__ does not do. 
    """
    path, filename = os.path.split(fullpath)
    filename, ext = os.path.splitext(filename)
    sys.path.append(path)
    module = __import__(filename)
    reload(module) # Might be out of date
    del sys.path[-1]
    return module


def submission_paths(submissions_folder):
    """Name the paths for results/grades files etc."""

    TEMP_USER_FOLDER = 'temp'
    RESULTS_FOLDER = 'results'
    DEFAULT_RESULT_PATTERN = 'result_%s.txt'
    DEFAULT_GRADES_PATTERN = 'grades_%s.txt'
    DEFAULT_STATS_PATTERN = 'stats_%s.txt'
    
    import time
    
    #
    # Create the results folder.
    #
    results_folder = os.path.join(submissions_folder, RESULTS_FOLDER)
    if not os.path.exists(results_folder):
        os.mkdir(results_folder)

    results_path = os.path.join(results_folder, DEFAULT_RESULT_PATTERN % time.strftime('%y%m%d_%H%M%S'))
    grades_path = os.path.join(results_folder, DEFAULT_GRADES_PATTERN % time.strftime('%y%m%d_%H%M%S'))
    stats_path = os.path.join(results_folder, DEFAULT_STATS_PATTERN % time.strftime('%y%m%d_%H%M%S'))
    temp_folder = os.path.join(submissions_folder, TEMP_USER_FOLDER)

    #
    # Create the column headers in the grade file
    #
    f_grades = open(grades_path, 'wb')
    f_grades.write('GRADE\tID\n')
    f_grades.close()
    
    return {'results_path':results_path, 'grades_path':grades_path, 'temp_folder':temp_folder, 'stats_path':stats_path}


def add_grade(submitters, test_result, grades_path):
    """Prepare the grades"""
    
    GRADE_FORMAT = '%d\t%s\n'

    grade = int(round(100 * test_result.successes / test_result.testsRun))

    grade_str = ''
    for submitter in submitters:
        id = submitter.split()[-1]
        grade_str += GRADE_FORMAT % (grade, id)

    f_grades = open(grades_path, 'ab')
    f_grades.write(grade_str)
    f_grades.close()


def add_stats(submitters, test_result, stats_path):
    """Add the statistics of the tests"""

    stats = test_result.testsStats
    keys = stats.keys()
    keys.sort()
    
    if not os.path.exists(stats_path):
        #
        # Create the top row with name of tests
        #
        f_stats = open(stats_path, 'ab')
        f_stats.write('\t%s\n' % '\t'.join([key.split('.')[-1] for key in keys]))
    else:
        f_stats = open(stats_path, 'ab')
            
    id = submitters[0].split()[-1]
    f_stats.write('%s\t%s\n' % (id, '\t'.join([str(stats[key]) for key in keys])))

    f_stats.close()


def get_submitters(temp_folder):
    
    import glob
    
    glob_result = glob.glob(os.path.join(temp_folder, '[sS]ubmitters.txt'))
    if not glob_result:
        raise Exception('Unable to find submitters.txt')
    
    sub_text = glob_result[0]
    sub_f = open(sub_text, 'rb')
    sub_data = sub_f.readlines()
    sub_f.close()
    
    submitters = [line.strip() for line in sub_data]
    submitters = [line for line in submitters if line != '']

    return submitters


def unzip_submission(submissions_folder, temp_folder, submission, f_results):
    
    import shutil

    SUBMISSION_HEADER = "\nSubmission by %s\n\n"
    
    #
    # Unzip the submission into a temporary path.
    #
    os.chdir(submissions_folder)
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)
    
    if os.system('unzip %s -d %s' % (submission, temp_folder)):
        raise Exception('Failed unzipping the submission')

    submitters = get_submitters(temp_folder)
    f_results.write(SUBMISSION_HEADER % ' & '.join(submitters))

    return submitters


def traverse_tree(root_pid):
    """Traverse a tree of processes starting from the root.
Return a list of all childs in reverse order (from bottom up) including the root_pid."""

    child_pids = []
    f = os.popen('ps -eo ppid,pid')
    for line in f.readlines():
        g = re.search(r"\s*(\d+)\s+(\d+)\s+.*", line)
        
        if not g or len(g.groups()) < 2 or int(g.groups()[0]) != root_pid:
            continue

        child_pids.append(int(g.groups()[1]))

    f.close()
    
    reverse_tree = []
    for cpid in child_pids:
        reverse_tree += traverse_tree(cpid)
        
    reverse_tree.append(root_pid)
    
    return reverse_tree
            

def get_orphan_pids():
    """Get orphan processes with the same cmd like the current process."""

    pids = []
    cmd = ''
    pid = os.getpid()
    
    f = os.popen('ps -eo ppid,pid,cmd')
    for line in f.readlines():
        g = re.search(r"(\d+)\s+(\d+)\s+(.*)", line.strip())
        
        if not g or len(g.groups()) < 3:
            continue
        
        pp, p, c = g.groups()
        
        if int(p) == pid:
            required_cmd = c
            continue

        if int(pp) == 1:
            pids.append((int(p), c))
             
    f.close()

    orphan_pids = [p for p, c in pids if c == required_cmd]

    return orphan_pids


#
# Watchdog utility globals
#
WD_DEVICE_PATH = '/dev/watchdog'
WD_MODULE_LOAD = 'wd_module_load %s' % os.path.join(BASE_INSTALL_PATH, WD_FILES_FOLDER)
WD_MODULE_UNLOAD = 'wd_module_unload'

class WatchDog(object):
    """A class that wraps the linux software watchdog"""
    def __init__(self, timeout=None):

        from hwgrader.watchdogdev import watchdog
        
        status = os.system(WD_MODULE_LOAD)
        if status:
            raise Exception('Failed loading the watchdog module, exit with status: %d, %d' % (status, status/256))
        
        self.wd = watchdog(WD_DEVICE_PATH)
        
        if timeout:
            self.wd.set_timeout(timeout)
        
    def __del__(self):
        self.close()

    def close(self):
        if self.wd:
            self.wd.magic_close()
            self.wd = None
            
            os.system(WD_MODULE_UNLOAD)
    
    
class RebootableTestSuite(unittest.TestSuite):
    """A special TestSuite that knows to handle reboots.
    """

    def __call__(self, result):
        
        past_tests_ids = result.get_tests_ids()
        tests = [test for test in self._tests if test.id() not in past_tests_ids]
         
        for test in tests:
            if result.shouldStop:
                break
            test(result)
            
        return result


class TestStatus(object):
    """Class that stores test status"""
    
    def __init__(self, path=TEST_STATUS_PATH, new=False):
        """
        Initialize the status possibly from file.
        """
        
        self._path = path
        
        if path and not new:
            f = open(path, 'rb')
            self._status = pickle.load(f)
            f.close()
        else:
            self._status = {'tests':[], 'successes':[], 'failures':[], 'errors':[], 'crashes_num':0}
    
        self._save()
        
    def _save(self):
        
        if not self._path:
            return
        
        f = open(self._path, 'wb')
        pickle.dump(self._status, f)
        f.close()
        
    #
    # Hanlde all errors/failures etc...
    #
    def addTest(self, test):
        self._status['tests'].append(test.id())
        self._save()
        
    def addEvent(self, event_name, event_value):
        self._status[event_name].append(event_value)
        self._save()

    def get_tests_ids(self):
        return self._status['tests']
    
    def get_errors(self):
        return self._status['errors']
    
    def get_failures(self):
        return self._status['failures']
    
    def get_crashes_num(self):
        return self._status['crashes_num']
    
    def get_successes(self):
        return self._status['successes']
    
    def startTest(self, test):
        """Called at the start of the test"""
        
        self.addTest(test)
        self._status['crashes_num'] += 1
        self._save()

    def stopTest(self, test):
        "Called when the given test has been run"
        
        self._status['crashes_num'] -= 1
        self._save()


#
# Paralelized unittest code
#
class ParTestResult(unittest.TestResult):
    """Holder for test result information.

    This class is cases when the test result should be shared
    across process. I.e. when a test forks a child process and
    this child adds an error, the parent process should be
    aware of this. This is done by pickling the status in a 
    file (instead of just a property of the class).
    """
    def __init__(self, test_status=None):
        self.shouldStop = 0

        if test_status is None:
            test_status = TestStatus(path=None)
            
        self.test_status = test_status

    def __del__(self):
        """Destructor."""

        #
        # Close the file descriptors.
        #
        self.closePipeRd()
        self.closePipeWr()

    def startTest(self, test):
        """Called at the start of the test"""
        
        self.test_status.startTest(test)
        
    def stopTest(self, test):
        "Called when the given test has been run"

        self.test_status.stopTest(test)        

    def wasSuccessful(self):
        "Tells whether or not this result was a success"
        return len(self.failures) == len(self.errors) == self.crashes_num == 0

    def createPipe(self):
        """Create the pipe that the test process uses to send errors through"""

        self.pr, self.pw = os.pipe()
        #
        # The writing side of the pipe is set to non block so that it doesn't
        # block if too many child precess fail and try to write. This causes
        # the buffer to get filled and when a child tries to write to a full
        # pipe, it is blocked
        #
        fcntl.fcntl(self.pw, fcntl.F_SETFL, os.O_NONBLOCK)
        
    def destroyPipe(self):
        """Read the contents of the pipe and close it."""

        self._unpickle_events()
        self.closePipeRd()
        self.closePipeWr()
        
    def closePipeRd(self):
        """Close the Read side of the Pipe"""
        
        if self.pr:
            os.close(self.pr)
            self.pr = None
        
    def closePipeWr(self):
        """Close the Write side of the Pipe"""
        
        if self.pw:
            os.close(self.pw)
            self.pw = None
        
    def _pickle_event(self, event_name, event_value):
        """Pickle the event (error, failure etc.) through the pipe"""

        if self.pw == None:
            #
            # The main process writes directly to the status dict
            # (It can't use the Wr side of the pipe).
            #
            self.test_status.addEvent(event_name, event_value)
        else:
            try:
                os.write(self.pw, pickle.dumps((event_name, event_value)))
            except OSError, e:
                #
                # The pipe is probably full (happens when many child process fail)
                #
                pass

    def _unpickle_events(self):
        """Unpickle events (error, failure etc.) through the pipe"""

        if self.pr == None:
            #
            # Alread read or slight chance that we are in a child process (should
            #  not read this side of the pipe)
            #
            return

        while 1:
            r, w, e, = select.select([self.pr], [], [], 0)
            if self.pr in r:
                #
                # This part is called when all child process have already closed their
                # write side, therefore the read should not block but throw an EOF error.
                # NOTE:
                # In some cases the test might create a segmentation fault leaving
                # the write side of the child's pipe open. This might cause the read
                # to wait infinitly. Therefore I check with select().
                #
                try:
                    event_name, event_value =  pickle.loads(os.read(self.pr, 10000))
                    self.test_status.addEvent(event_name, event_value)
                except EOFError:
                    break
            else:
                break

    def addError(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info().
        """
        self._pickle_event('errors', (test, self._exc_info_to_string(err)))

    def addFailure(self, test, err):
        """Called when an error has occurred. 'err' is a tuple of values as
        returned by sys.exc_info()."""
        self._pickle_event('failures', (test, self._exc_info_to_string(err)))

    def addSuccess(self, test):
        "Called when a test has completed successfully"
        self._pickle_event('successes', test.id())
        
    def _get_errors(self):
        return self.test_status.get_errors()
    
    errors = property(fget=_get_errors)
    
    def _get_failures(self):
        return self.test_status.get_failures()
    
    failures = property(fget=_get_failures)
    
    def _get_crashes_num(self):
        return self.test_status.get_crashes_num()
    
    crashes_num = property(fget=_get_crashes_num)
    
    def _get_successes(self):
        return len(self.test_status.get_successes())
    
    successes = property(fget=_get_successes)

    def _get_testsStats(self):
        """Return a dict listing the tests run and their success/failure status"""

        res = {}
        for test_id in self.test_status.get_tests_ids():
            res[test_id] = False

        for test_id in self.test_status.get_successes():
            res[test_id] = True

        return res

    testsStats = property(fget=_get_testsStats)

    def _tests_run(self):
        return len(self.test_status.get_tests_ids())
    
    testsRun = property(fget=_tests_run)
 
    def get_tests_ids(self):
        return self.test_status.get_tests_ids()

    def __repr__(self):
        return "<%s run=%i errors=%i failures=%i, crashes=%i>" % \
               (self.__class__, self.testsRun, len(self.errors),
                len(self.failures), self.crashes_num)


class _ParTextTestResult(ParTestResult):
    """A test result class that can print formatted text results to a stream.

    Used by TextTestRunner.
    """
    
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, stream, descriptions, verbosity, test_status=None):
        ParTestResult.__init__(self, test_status)
        self.stream = stream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions

    def getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def startTest(self, test):
        ParTestResult.startTest(self, test)
        if self.showAll:
            self.stream.write(self.getDescription(test))
            self.stream.write(" ... ")
        self.stream.flush()

    def addSuccess(self, test):
        ParTestResult.addSuccess(self, test)
        if self.showAll:
            self.stream.writeln("ok")
        elif self.dots:
            self.stream.write('.')
        self.stream.flush()

    def addError(self, test, err):
        ParTestResult.addError(self, test, err)
        if self.showAll:
            self.stream.writeln("ERROR")
        elif self.dots:
            self.stream.write('E')
        self.stream.flush()

    def addFailure(self, test, err):
        ParTestResult.addFailure(self, test, err)
        if self.showAll:
            self.stream.writeln("FAIL")
        elif self.dots:
            self.stream.write('F')
        self.stream.flush()
        
    def printErrors(self):
        if self.dots or self.showAll:
            self.stream.writeln()
        self.printErrorList('ERROR', self.errors)
        self.printErrorList('FAIL', self.failures)
        self.stream.flush()

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err)

    def log(self, msg):
        self.stream.writeln(msg)
        self.stream.flush()


class ParTextTestRunner(object):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1, test_status=None):
        self.stream = unittest._WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.test_status = test_status

    def _makeResult(self):
        return _ParTextTestResult(self.stream, self.descriptions, self.verbosity, self.test_status)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = float(stopTime - startTime)
        result.printErrors()
        self.stream.writeln(result.separator2)
        run = result.testsRun
        self.stream.writeln("Ran %d test%s in %.3fs" %
                            (run, run == 1 and "" or "s", timeTaken))
        self.stream.writeln()
        if not result.wasSuccessful():
            self.stream.write("FAILED (")
            failed, errored = map(len, (result.failures, result.errors))
            crashes_num = result.crashes_num
            
            if failed:
                self.stream.write("failures=%d" % failed)
            if errored:
                if failed: self.stream.write(", ")
                self.stream.write("errors=%d" % errored)
            if crashes_num > 0:
                if failed or errored: self.stream.write(", ")
                self.stream.write("crashes=%d" % crashes_num)
                
            self.stream.writeln(")")
        else:
            self.stream.writeln("OK")
        return result


class ParTestCase(unittest.TestCase):
    """A class whose instances are single test cases.

    The ParTestCase starts a new process for each test
    this enables the isolation of tests one from the other.
    """

    def __init__(self, methodName='runTest'):
        """Create an instance of the class that will use the named test
           method when executed. Raises a ValueError if the instance does
           not have a method with the specified name.
        """
        try:
            self.__testMethodName = methodName
            testMethod = getattr(self, methodName)
            self.__testMethodDoc = testMethod.__doc__
        except AttributeError:
            raise ValueError, "no such test method in %s: %s" % \
                  (self.__class__, methodName)

    def shortDescription(self):
        """Returns a one-line description of the test, or None if no
        description has been provided.

        The default implementation of this method returns the first line of
        the specified test method's docstring.
        """
        doc = self.__testMethodDoc
        return doc and string.strip(string.split(doc, "\n")[0]) or None

    def id(self):
        return "%s.%s" % (self.__class__, self.__testMethodName)

    def __str__(self):
        return "%s (%s)" % (self.__testMethodName, self.__class__)

    def __repr__(self):
        return "<%s testMethod=%s>" % \
               (self.__class__, self.__testMethodName)

    def __call__(self, result=None):
        if result is None: result = self.defaultTestResult()
        result.startTest(self)
        testMethod = getattr(self, self.__testMethodName)
        try:
            result.createPipe()
            tpid = os.fork()
            if tpid == 0:
                #
                # The child processes should close the read side of the pipe.
                #
                result.closePipeRd()
                
                try:
                    self.setUp()
                except KeyboardInterrupt:
                    os._exit(-1)
                except:
                    result.addError(self, self.__exc_info())
                    os._exit(0)

                ok = 0
                try:
                    testMethod()
                    ok = 1
                except self.failureException, e:
                    result.addFailure(self, self.__exc_info())
                except KeyboardInterrupt:
                    os._exit(-1)
                except:
                    result.addError(self, self.__exc_info())

                try:
                    self.tearDown()
                except KeyboardInterrupt:
                    os._exit(-1)
                except:
                    result.addError(self, self.__exc_info())
                    ok = 0

                if ok:
                    result.addSuccess(self)

                #
                # IMPORTANT NOTE:
                # child processses of the test processes (tpid), can throw
                # exceptions either explicitly or implicitly through assert_
                # and other unittest functions. This means that they reach
                # the os._exit command below. This exit command avoids that
                # the exceptions propogate further 'up' in the code.
                #
                os._exit(0)

            #
            # The parent process should close the write side of the pipe.
            #
            result.closePipeWr()

            #
            # Set the watchdog
            #
            test_timeout = getattr(self, '_TEST_TIMEOUT', TEST_TIMEOUT)
            wd = WatchDog(timeout=test_timeout)
            
            try:
                try:
                    cpid, status = os.waitpid(tpid, 0)
                except KeyboardInterrupt:
                    raise
                except:
                    result.addError(self, self.__exc_info())
            finally:
                #
                # Turn of the watchdog
                #
                wd.close()
                
            #
            # Check the exit status. This part is wraped in a try caluse
            # so that I can use the addError method.
            #    
            try:
                if os.WIFEXITED(status) and os.WEXITSTATUS(status) != 0:
                    if os.WEXITSTATUS(status) == 255:
                        raise KeyboardInterrupt
                    else:
                        raise TestError, 'The test process exited unexpectedly with code %d' % (os.WEXITSTATUS(status) - 256)
                    
                if os.WIFSTOPPED(status):
                    sig = os.WSTOPSIG(status)
                    if sig in SIGNALS_DICT.keys():
                        sig_str = '%s(%d)' % (SIGNALS_DICT[sig], sig)
                    else:
                        sig_str = 'None(%d)' % sig
                        
                    raise TestError, 'The test process stopped unexpectedly by signal %s' % sig_str
                
                if os.WIFSIGNALED(status):
                    sig = os.WTERMSIG(status)
                    if sig in SIGNALS_DICT.keys():
                        sig_str = '%s(%d)' % (SIGNALS_DICT[sig], sig)
                    else:
                        sig_str = 'None(%d)' % sig
                        
                    raise TestError, 'The test process terminated unexpectedly by signal %s' % sig_str

            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self.__exc_info())
        finally:
            result.destroyPipe()
            
            #
            # Remove any orphan process that the test might have left.
            # The orphan processes are identified as python processes
            # that are childs of process 1 and have the same cmd.
            # TODO:
            # Add an error where there are orphans left.
            #
            orphan_pids = get_orphan_pids()
            
            for cpid in orphan_pids:
                os.kill(cpid, signal.SIGKILL)

            result.stopTest(self)

    def debug(self):
        """Run the test without collecting errors in a TestResult"""
        self.setUp()
        getattr(self, self.__testMethodName)()
        self.tearDown()

    def __exc_info(self):
        """Return a version of sys.exc_info() with the traceback frame
           minimised; usually the top level of the traceback frame is not
           needed.
        """
        exctype, excvalue, tb = sys.exc_info()
        if sys.platform[:4] == 'java': ## tracebacks look different in Jython
            return (exctype, excvalue, tb)
        newtb = tb.tb_next
        if newtb is None:
            return (exctype, excvalue, tb)
        return (exctype, excvalue, newtb)

    def errnoCheck(self, cmd, args=(), kwds={}, expected_errno=0, msg='Operation did not throw an OSError'):
        """Run a cmd that is expected to throw a OSError with code errno. Useful for testing error handling.
        
        Params:
        -------
        cmd - The command to run
        args, kwds - Arguments that are passed to the cmd as arguments.
        expected_errno - Expected errno code, either an int or a tuple of several possible errnos.
        msg - Error message to show when no error is thrown
        """
        
        exception_thrown = False
        try:
            cmd(*args, **kwds)
        except IOError, e:
            exception_thrown = True
        except OSError, e:
            exception_thrown = True

        self.assert_(exception_thrown, msg)
        self.assert_(e.errno in errno.errorcode, 'Unkonwn errno code: %d' % e.errno)
        
        if isinstance(expected_errno, int):
            #
            # Expecting a single error code
            #
            self.assertEqual(e.errno, expected_errno, 'Wrong errno code: %s, (expecting %s)' % (errno.errorcode[e.errno], errno.errorcode[expected_errno]))   
        else:
            #
            # Expecting one of several possible error codes
            #
            self.assert_(e.errno in expected_errno, 'Wrong errno code: %s, (expecting one of {%s})' % (errno.errorcode[e.errno], ','.join([errno.errorcode[err] for err in expected_errno])))


def set_grub(custom=False):
    """Set the grub to the desired kernel"""
    
    f_grub = open(GRUB_PATH, 'rb')
    grub_lines = f_grub.readlines()
    f_grub.close()
    
    kernels = []
    for line in grub_lines:
        if re.match('title', line):
            kernels.append(line.split()[-1])
    
    default_line = 0
    for line in grub_lines:
        if re.match('default=', line):
            break
        default_line += 1
    
    if default_line > len(grub_lines):
        raise "Unable to set the defulat line in grub.conf"
    
    if re.search('custom', kernels[0]):
        custom_index = 0
    else:
        custom_index = 1
        
    if custom:
        grub_lines[default_line] = 'default=%d\n' % custom_index
    else:
        grub_lines[default_line] = 'default=%d\n' % (1-custom_index)
        
    f_grub = open(GRUB_PATH, 'wb')
    f_grub.writelines(grub_lines)
    f_grub.close()


def init_bash(script_path):
    """Create a backup of .bash_profile and add this script to the end of .bash_profile"""
    
    shutil.copyfile(BASH_PROFILE_PATH, BASH_PROFILE_BAKCUP_PATH)
    
    f_bash = open(BASH_PROFILE_PATH, 'a')
    f_bash.write('\n%s\n' % script_path)
    f_bash.close()
        

def init_sysctl():
    """Create a backup of sysctl.conf and set the kernel.panic field to reboot after panic"""
    
    shutil.copyfile(SYSCTL_PATH, SYSCTL_BAKCUP_PATH)
    
    for line in fileinput.input(SYSCTL_PATH, inplace=1):
        if line.find(KERNEL_PANIC_STR) < 0:
            sys.stdout.write(line)

    f_sysctl = open(SYSCTL_PATH, 'ab')
    f_sysctl.write('%s=%d\n' % (KERNEL_PANIC_STR, KERNEL_PANIC_TIMEOUT))
    f_sysctl.close()
        

def init_autologin():
    """Copy the autologin files"""
    
    shutil.copyfile('/etc/inittab', os.path.join(TEMP_FILES_FOLDER, 'inittab'))
    shutil.copyfile('/etc/login.defs', os.path.join(TEMP_FILES_FOLDER, 'login.defs'))
    
    autologin_path = os.path.join(BASE_INSTALL_PATH, AUTOLOGIN_FILES_FOLDER)

    shutil.copyfile(os.path.join(autologin_path, 'inittab_autologin'), '/etc/inittab')
    shutil.copyfile(os.path.join(autologin_path, 'login.defs_autologin'), '/etc/login.defs')
    
    for line in fileinput.input('/etc/inittab', inplace=1):
        sys.stdout.write(line.replace(INITTAB_TEMPLATE, autologin_path))


def init_grader(submissions_folder, test_path, break_flag, kernel_test):
    """Prepare the system for the grader boot loop"""
    
    if os.path.exists(TEMP_FILES_FOLDER):
        raise Exception('Temporary grader files remain from previous run. This might indicate a bad exit.\nIt is suggested to run the script with -r flag.')

    os.mkdir(TEMP_FILES_FOLDER)

    script_path = os.path.abspath(sys.argv[0])
    
    init_bash(script_path)
    init_sysctl()
    init_autologin()

    if kernel_test:
        set_grub(custom=False)
    
    paths = submission_paths(submissions_folder)
    
    #
    # Save the configuration of the grader
    #
    f = open(GRADER_CONFIG_PATH, 'wb')
    config = ConfigParser.ConfigParser()
    config.add_section('paths')
    config.set('paths', 'submissions_folder', submissions_folder)
    config.set('paths', 'test_path', test_path)
    config.set('paths', 'results_path', paths['results_path'])
    config.set('paths', 'grades_path', paths['grades_path'])
    config.set('paths', 'stats_path', paths['stats_path'])
    config.set('paths', 'temp_folder', paths['temp_folder'])
    config.add_section('flags')
    config.set('flags', 'break_flag', break_flag)
    config.write(f)
    f.close()

    #
    # Create a list of submissions to run
    #
    sub_list = glob.glob(os.path.join(submissions_folder, '*.[zZ][iI][pP]'))
    sub_state = {
        'list': sub_list,
        'index': 0
    }
    f_sub = open(SUBMISSION_STATE_PATH, 'wb')
    pickle.dump(sub_state, f_sub)
    f_sub.close()

    #
    # Make a copy of the custom kernel
    #
    if kernel_test:
        shutil.os.rename(CUSTOM_KERNEL_PATH, CUSTOM_KERNEL_BAKCUP_PATH)


def end_bash():
    """Restore the backup of .bash_profile."""
    
    try:
        shutil.os.rename(BASH_PROFILE_BAKCUP_PATH, BASH_PROFILE_PATH)
    except:
        warnings.warn('Missing .bash_profile backup')


def end_sysctl():
    """Restore the backup of sysctl.conf."""
    
    try:
        shutil.os.rename(SYSCTL_BAKCUP_PATH, SYSCTL_PATH)
    except:
        warnings.warn('Missing sysctl.conf backup')


def end_autologin():
    """Restore the autologin files"""
    
    try:
        shutil.os.rename(os.path.join(TEMP_FILES_FOLDER, 'inittab'), '/etc/inittab')
    except:
        warnings.warn('Missing inittab backup')
    try:
        shutil.os.rename(os.path.join(TEMP_FILES_FOLDER, 'login.defs'), '/etc/login.defs')
    except:
        warnings.warn('Missing login.defs backup')
    

def end_grader():
    """Remove the grader loop from the system"""
    
    end_bash()
    end_sysctl()
    end_autologin()

    if os.path.exists(CUSTOM_KERNEL_BAKCUP_PATH):
        if os.path.exists(CUSTOM_KERNEL_PATH):
            shutil.rmtree(CUSTOM_KERNEL_PATH)
        shutil.os.rename(CUSTOM_KERNEL_BAKCUP_PATH, CUSTOM_KERNEL_PATH)

    if os.path.exists(TEMP_FILES_FOLDER):
        shutil.rmtree(TEMP_FILES_FOLDER, ignore_errors=True)


def next_submission(submissions_folder):
    """Get the next submission"""

    f_sub = open(SUBMISSION_STATE_PATH, 'rb')
    sub_state = pickle.load(f_sub)
    f_sub.close()

    if len(sub_state['list']) <= sub_state['index']:
        submission = None
    else:
        submission = sub_state['list'][sub_state['index']]

        f_sub = open(SUBMISSION_STATE_PATH, 'wb')
        sub_state['index'] = sub_state['index']+1
        pickle.dump(sub_state, f_sub)
        f_sub.close()

    return submission



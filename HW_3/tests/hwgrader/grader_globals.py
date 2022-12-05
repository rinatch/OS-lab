import os

#
# Some defaults/globals
#
MMLOG_FILES_FOLDER = 'mmlog_files'
KERNEL_MODIFICATIONS_FOLDER = 'kernel_modifications'
BUILD_SCRIPT = 'build_submission.sh'
BUILD_NM_SCRIPT = 'build_submission_no_modules.sh'
AUTOLOGIN_FILES_FOLDER = 'autologin_files'
BASE_INSTALL_PATH = '/etc/hwgrader'
BASH_PROFILE_PATH = os.path.expanduser('~/.bash_profile')
TEMP_FILES_FOLDER = os.path.expanduser('~/temp_grader')
BASH_PROFILE_BAKCUP_PATH = os.path.join(TEMP_FILES_FOLDER, '.bash_profile')
SYSCTL_PATH = os.path.expanduser('/etc/sysctl.conf')
SYSCTL_BAKCUP_PATH = os.path.join(TEMP_FILES_FOLDER, 'sysctl.conf')
KERNEL_PANIC_STR = 'kernel.panic'
KERNEL_PANIC_TIMEOUT = 10
SUBMISSION_STATE_PATH = os.path.join(TEMP_FILES_FOLDER, 'sub_state.pkl')
GRUB_PATH = '/boot/grub/grub.conf'
TEST_STATUS_PATH = os.path.join(TEMP_FILES_FOLDER, 'test_status.pkl')
GRADER_CONFIG_PATH = os.path.join(TEMP_FILES_FOLDER, 'config_grader')
INITTAB_TEMPLATE = 'BIN_PATH'
DEFAULT_SUBMISSIONS_FOLDER = '/mnt/hgfs/Shared/submissions'
DEFAULT_TESTS_FOLDER = os.path.expanduser('~/tests')
DEFAULT_TEST_NAME = 'hw_test.py'
CUSTOM_KERNEL_PATH = '/usr/src/linux-2.4.18-14custom'
CUSTOM_KERNEL_BAKCUP_PATH = os.path.join(TEMP_FILES_FOLDER, os.path.split(CUSTOM_KERNEL_PATH)[-1])
WD_FILES_FOLDER = 'wd_files'
MAKE_FILE = 'Makefile'

#
# Tests timeout after TEST_TIMEOUT seconds
#
TEST_TIMEOUT = 200 #60

#
# Memory log utility globals
#
MMLOG_DEVICE_PATH = '/dev/mmlog_device'
MMLOG_MODULE_LOAD = 'mmlog_module_load %s' % os.path.join(BASE_INSTALL_PATH, MMLOG_FILES_FOLDER)
MMLOG_MODULE_UNLOAD = 'mmlog_module_unload'


#!/usr/bin/python

# Simple script to validate correct submission format

import shutil
import sys
import re
import os


def get_submitters(temp_folder):
    submitters_filename = os.path.join(temp_folder, 'submitters.txt')
    if not os.path.exists(submitters_filename):
        raise Exception('Unable to find submitters.txt - Invalid format')

    if not os.path.exists(os.path.join(temp_folder, 'procenet_api.h')):
        raise Exception('No procenet_api.h file - Invalid format')

    sub_f = open(submitters_filename, 'rb')
    sub_data = sub_f.readlines()
    sub_f.close()

    submitters = [line.strip() for line in sub_data]
    submitters = [line for line in submitters if line != '']
    print 'Validate format success - please make sure your code compiles and you submit your *final* version!'
    print 'Tip: use the make_changed.py script to validate your extracted zip will compile sucessfully in the VM'
    print 'Submitter A: ' + submitters[0]
    print 'Submitter B: ' + submitters[1]


def unzip_submission(submission_file):

    import shutil

    SUBMISSION_HEADER = "\nSubmission by %s\n\n"
    temp_folder = '/home/user/temp_grader'

    #
    # Unzip the submission into a temporary path.
    #
    os.chdir(os.path.dirname(submission_file))
    if os.path.exists(temp_folder):
        shutil.rmtree(temp_folder, ignore_errors=True)

    if os.system('unzip -q %s -d %s' % (submission_file, temp_folder)):
        raise Exception('Failed unzipping the submission - Invalid format')

    get_submitters(temp_folder)


if __name__ == '__main__':
    submissions_folder = os.path.abspath(sys.argv[1])
    unzip_submission(submissions_folder)

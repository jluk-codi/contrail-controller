#
# Copyright (c) 2013 Juniper Networks, Inc. All rights reserved.
#
from setuptools import setup, find_packages, Command
import os, sys, re

class RunTestsCommand(Command):
    description = "Test command to run testr in virtualenv"
    user_options = [
        ('coverage', 'c',
         "Generate code coverage report"),
        ]
    boolean_options = ['coverage']
    def initialize_options(self):
        self.cwd = None
        self.coverage = False
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        logfname = 'test.log'
        args = '-V'
        if self.coverage:
            logfname = 'coveragetest.log'
            args += ' -c'
        rc_sig = os.system('./run_tests.sh %s' % args)
        if rc_sig >> 8:
            os._exit(rc_sig>>8)
        with open(logfname) as f:
            if not re.search('\nOK', ''.join(f.readlines())):
                os._exit(1)

setup(
    name='tungsten_issu',
    version='0.1dev',
    packages=find_packages(),
    package_data={'': ['*.html', '*.css', '*.xml']},
    zip_safe=False,
    long_description="VNC Tungsten ISSU",
    entry_points = {
         # Please update sandesh/common/vns.sandesh on process name change
         'console_scripts' : [
             'tungsten-issu-pre-sync = tungsten_issu.issu_tungsten_pre_sync:_issu_cassandra_pre_sync_main',
             'tungsten-issu-run-sync = tungsten_issu.issu_tungsten_run_sync:_issu_rmq_main',
             'tungsten-issu-post-sync = tungsten_issu.issu_tungsten_post_sync:_issu_cassandra_post_sync_main',
             'tungsten-issu-zk-sync = tungsten_issu.issu_tungsten_zk_sync:_issu_zk_main',
         ],
    },
    install_requires=[
        'jsonpickle'
    ],
    cmdclass={
       'run_tests': RunTestsCommand,
    },
)

#
# Copyright (c) 2014 Juniper Networks, Inc.
#

import setuptools


def requirements(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

setuptools.setup(
    name='Tungsten Fabric-vrouter-netns',
    version='0.1',
    packages=setuptools.find_packages(),

    # metadata
    author="Tungsten Fabric",
    author_email="dev@lists.tungsten.io",
    license="Apache Software License",
    url="http://www.tungsten.io/",
    long_description="Script to manage Linux network namespaces",

    install_requires=requirements('requirements.txt'),

    test_suite='Tungsten Fabric_vrouter_netns.tests',
    tests_require=requirements('test-requirements.txt'),

    entry_points = {
        'console_scripts': [
            'Tungsten Fabric-vrouter-netns = Tungsten Fabric_vrouter_netns.vrouter_netns:main',
            'Tungsten Fabric-vrouter-docker = Tungsten Fabric_vrouter_netns.vrouter_docker:main',
            'netns-daemon-start = Tungsten Fabric_vrouter_netns.daemon_start:daemon_start',
            'netns-daemon-stop = Tungsten Fabric_vrouter_netns.daemon_stop:daemon_stop'
        ],
    },
)

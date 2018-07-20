#
# Copyright (c) 2017 Juniper Networks, Inc.
#

import setuptools

setuptools.setup(
    name='tungsten-vrouter-provisioning',
    version='0.1dev',
    packages=setuptools.find_packages(),

    # metadata
    author="Tungsten Fabric",
    author_email="dev@lists.tungsten.io",
    license="Apache Software License",
    url="http://www.tungsten.io/",
    long_description="Tungsten compute provisioning module",
    entry_points={
        'console_scripts': [
            'tungsten-compute-setup = tungsten_vrouter_provisioning.setup:main',
            'tungsten-toragent-setup = tungsten_vrouter_provisioning.toragent.setup:main',
            'tungsten-toragent-cleanup = tungsten_vrouter_provisioning.toragent.cleanup:main',
            ],
    },
)

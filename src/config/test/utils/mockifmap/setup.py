#!/usr/bin/env python

from distutils.core import setup

setup(name='mockifmap',
      version='1.0',
      description='IFMAP Distribution Utilities for systest',
      author='tungsten',
      author_email='tungsten-sw@juniper.net',
      url='http://tungsten.io/',
      packages=['mockifmap', ],
      data_files=[('lib/python2.7/site-packages/mockifmap', ['ifmap.properties','basicauthusers.properties','publisher.properties']),],
     )

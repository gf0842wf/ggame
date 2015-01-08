#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import gnet

setup(
      name='gnet',
      version='0.1.0',
      description='gevent server protocol and factory',
      author='fk',
      author_email='gf0842wf@gmail.com',
      packages=['gnet', 'gnet.db'],
      package_data={'': ['README.md']},
      license='MIT',
      classifiers=[
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   ],
      test_suite = 'tests',
     )
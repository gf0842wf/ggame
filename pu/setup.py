#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import pu

setup(
      name='pu',
      version='0.1.0',
      description='python utils',
      author='fk',
      author_email='gf0842wf@gmail.com',
      packages=['pu', 'pu.adt', 'pu.pattern'],
      package_data={'': ['README.md']},
      license='MIT',
      classifiers=[
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   ],
      test_suite = 'tests',
     )
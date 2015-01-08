#!/usr/bin/python
# -*- coding: utf-8 -*-
from distutils.core import setup, Extension
 
__version__ = "0.1.0"
 
macros = [('MODULE_VERSION', '"%s"' % __version__)]
 
setup(name="xorcrypt",
      version=__version__,
      author="fk",
      author_email='gf0842wf@gmail.com',
      description="xor encrypt/decrypt for python",
      platforms=["Platform Independent"],
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules"
      ],
      ext_modules=[
        Extension(name='xorcrypt', sources=['xorcrypt.c'], define_macros=macros)
      ]
)

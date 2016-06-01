#!/usr/bin/env python

import os
from setuptools import setup, find_packages

DESCRIPTION = "Error propgation calculations with uncertian quantities."
LONG_DESCRIPTION = open('README.md').read()

setup(name='pyErrorProp',
      version='0.0.0',
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='C.D. Clark III',
      url='https://github.com/CD3/pyErrorProp',
      license="MIT License",
      platforms=["any"],
      packages=['pyErrorProp']
     )

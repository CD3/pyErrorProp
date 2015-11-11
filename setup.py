#!/usr/bin/env python

import os
from setuptools import setup, find_packages
import versioneer

DESCRIPTION = "Error propgation calculations with uncertian quantities."
LONG_DESCRIPTION = open('README.md').read()

scripts = [ os.path.join('scripts',f) for f in os.listdir('scripts/') if not f.startswith('.') ]
setup(name='pyErrorProp',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      author='C.D. Clark III',
      url='https://github.com/CD3/pyLabCalc',
      license="MIT License",
      platforms=["any"],
      packages=find_packages(),
      scripts=scripts
     )

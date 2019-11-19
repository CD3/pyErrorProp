import os
from setuptools import setup, find_packages

DESCRIPTION = "Error propgation calculations with uncertian quantities."
LONG_DESCRIPTION = open('README.md').read()
VERSION = '3.1.2'

setup(
  name = 'pyErrorProp',
  packages = ['pyErrorProp'],
  version = VERSION,
  license='MIT',
  description = DESCRIPTION,
  long_description = LONG_DESCRIPTION,
  author = 'CD Clark III',
  author_email = 'clifton.clark@gmail.com',
  url = 'https://github.com/CD3/pyErrorProp',
  download_url = f'https://github.com/CD3/pyErrorProp/archive/{VERSION}.tar.gz',
  keywords = ['physics', 'uncertainty', 'units'],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
  ],
)

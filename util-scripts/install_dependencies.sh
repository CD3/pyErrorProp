#! /bin/bash

deps="pytest pint uncertainties numpy mpmath"

for dep in $deps
do
  pip install $dep
done

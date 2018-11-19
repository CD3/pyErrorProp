#! /bin/bash

ROOTDIR=$(git rev-parse --show-toplevel || echo $PWD)
deps="$(cat ${ROOTDIR}/requirements.txt)"

for dep in $deps
do
  pip install $dep
done

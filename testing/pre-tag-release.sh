#! /bin/bash

# this script should run tests we want to make sure pass before tagging
# a release.

set -e # exist immediatly on error

ROOTDIR=$(git rev-parse --show-toplevel || echo $PWD)
cd $ROOTDIR

# make sure unit tests pass
./util-scripts/run_tests.sh




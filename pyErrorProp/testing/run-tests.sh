#! /bin/bash

dir=$(dirname $0)
opts=$*

export PYTHONPATH="$dir/../"
py.test -v $opts $dir


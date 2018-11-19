#! /bin/bash

sudo docker run --rm -v $PWD:/var/repo pyerrorprop-testing-3.6:latest "$@"
sudo docker run --rm -v $PWD:/var/repo pyerrorprop-testing-2.7:latest "$@"

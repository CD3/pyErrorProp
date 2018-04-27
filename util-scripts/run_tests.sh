#! /bin/bash

docker run --rm -v $PWD:/var/repo pyerrorprop-testing-3.6:latest
docker run --rm -v $PWD:/var/repo pyerrorprop-testing-2.7:latest

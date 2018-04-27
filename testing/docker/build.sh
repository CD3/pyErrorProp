#! /bin/bash

for file in Dockerfile-*
do
  tag=$(echo $file | sed "s/Dockerfile-//")
  docker build -t $tag -f ${file} .
done

#! /bin/bash

for file in Dockerfile-*
do
  tag=$(echo $file | sed "s/Dockerfile-//")
  sudo docker build -t $tag -f ${file} .
done

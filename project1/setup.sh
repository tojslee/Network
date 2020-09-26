#!/bin/bash

echo `apt-get install gcc`
echo `apt-get install libpcap-dev`
echo `gcc -o project project.c -lpcap`
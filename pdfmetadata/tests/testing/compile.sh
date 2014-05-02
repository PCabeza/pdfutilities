#! /bin/bash

gcc -c -O2 -o test.o test.c
gcc test.o -lgs
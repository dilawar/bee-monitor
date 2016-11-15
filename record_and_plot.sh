#!/bin/bash
set -x 

if [ $# -lt 1 ]; then
    python ./arduino_live -h 
    exit
fi
(
    python ./arduino_live "$@"  
)

#!/bin/bash - 
#===============================================================================
#
#          FILE: run.sh
# 
#         USAGE: ./run.sh 
# 
#   DESCRIPTION:  Run the whole setup.
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Dilawar Singh (), dilawars@ncbs.res.in
#  ORGANIZATION: NCBS Bangalore
#       CREATED: 09/29/2016 04:38:58 PM
#      REVISION:  ---
#===============================================================================

set -x
set -e
set -o nounset                              # Treat unset variables as an error

PORT=$(bash ./list_serial_ports.sh)
./build_and_upload.sh $PORT
python monitor.py -p $PORT

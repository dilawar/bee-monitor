#!/usr/bin/env python2

"""
monitor

Read the data from serial port and plot it using gnuplot.

"""
from __future__ import print_function
    
__author__           = "Dilawar Singh, Ananthamurhty, and Shriya P"
__copyright__        = "Copyright 2015, Bhalla lab, NCBS Bangalore"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = __author__
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import arduino 
import os
import sys
import time
import readchar

from collections import defaultdict
import datetime
import csv
import numpy as np
import codecs
import gnuplotlib 

running_trial_ = 0
save_dir_ = '_data'
trialNum = 0
serial_port_ = None
# How many crosses.
crosses_ = 0
args_ = None

def trial_file_path( trialNum ):
    return os.path.join( save_dir_, 'Trial%s.csv' % trialNum )

def cleanup():
    global gp_
    print("+++++++++++++++++++++++++++++ All over")
    gp_.__del__( )
    raise KeyboardInterrupt("Finished all")

def init_serial( args, baudRate = 38400):
    print( args )
    global serial_port_ 
    if args.port is None:
        args.port = arduino.get_default_serial_port( )
    serial_port_ = arduino.ArduinoPort( args.port, baudRate )
    serial_port_.open( wait = True )

def append_trial_data( outfile, data):
    with open(outfile, 'a') as f:
        msg = ",".join( [str(x) for x in data] )
        f.write( msg + '\n' )

def line_to_data( line ):
    """Convert read line to valid data.
    If >>> is in the line, print it onto console. THis is command response 
    from arduino.
    """
    data = [ ]
    if '>>>' in line:
        print(line)
        return data

    secs  = filter( None, line.split(',') )
    for i, x in enumerate( secs ):
        try:
            data.append( float(x.strip()) )
        except Exception as e:
            data = None
    # print( data )
    return data

def init_gui():
    text_.set_text('')
    return gline_, gline1_, text_

def countCrossing( vecs, state ):
    global crosses_
    maxThres = max( vecs ) * 0.75
    assert len( state ) >= len( vecs )
    for i, v in enumerate( vecs ):
        if v < 5 and not state[i]:
            state[i] = True
        elif v > 15 and state[i]:
            crosses_ += 1
            state[i] = False
    return state

def collectAndPlot( ):
    global q_
    global running_data_line_
    global current_state_
    global crosses_
    tstart = time.time()
    trialFile = trial_file_path( 0 )
    tvec, yvec = [], []
    crossStart, crossEnd = False, False
    # Maximum pins are 12.
    states = [ False ] * 12
    while True:
        line = serial_port_.read_line()
        data = line_to_data(line)
        if data is None:
            continue

        try:
            t, vs = float(data[0]), data[1:]
        except Exception as e:
            continue

        tvec.append( t )
        yvec.append( sum(vs) )
        states = countCrossing( vs, states )
        # modify data[0] to write to file.
        data[0] = datetime.datetime.now().isoformat( )
	data.append( crosses_ )
        append_trial_data(trialFile, data)
        title = '%s %2.2f %d' % ( args.port , time.time() - tstart, crosses_ )
        if len( yvec ) % 10 == 0:
            try:
                N = 100
                x, y = np.array( tvec[-N:] ), np.array( yvec[-N:] )
                gnuplotlib.plot( ( x, y ), title = title , terminal = 'x11' 
                         , yrange = [ 0, 500 ]
                        )
                            
            except Exception as e:
                print( "Couln't plot : %s" % e )

def init( args ):
    """
    Wait for first four questions to appear which requires writing to serial
    port. If serial port is sending legal data then continue, questions are
    probably answered.
    """
    global save_dir_ 
    global args_ 
    args_ = args
    now = datetime.datetime.now()
    timeStamp =  now.strftime('%Y-%m-%d_%H-%M-%S')
    outdir = 'Bee%s' % timeStamp
    save_dir_ = os.path.join( save_dir_, outdir )
    if os.path.exists(save_dir_):
        save_dir_ = os.path.join(save_dir_, timeStamp)
        os.makedirs(save_dir_)
    else:
        os.makedirs(save_dir_) 

    print( '[INFO] Init is done' )


def main( args  ):
    init( args  )
    print( '[INFO] Init is done' )
    collectAndPlot( )

if __name__ == '__main__':
    import argparse
    # Argument parser.

    description = '''Animate arduino data from serial port'''
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--port', '-p'
        , required = False
	, default = '/dev/ttyACM0'
        , help = 'Serial port [full path]'
        )

    args = parser.parse_args(  )
    init_serial( args )
    # Intialize logger after intializing serial port.
    try:
        main( args )
    except KeyboardInterrupt as e:
        cleanup()
        quit()


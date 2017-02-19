#!/usr/bin/env python

"""analyze.py: 


"""
    
__author__           = "Me"
__copyright__        = "Copyright 2016, Me"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Me"
__email__            = ""
__status__           = "Development"

import sys
import os
from datetime import datetime, timedelta
import numpy as np
import pandas
from collections import defaultdict
import pylab
pylab.style.use( 'ggplot' )

__fmt__ = "%Y-%m-%dT%H:%M:%S.%f"
__offset__ = 5.5            # IST +5:30
infile_ = None
ncols = 9

# how many crossing each hole
holes = defaultdict( list )
allCrossingTimes = []

args_ = None

def getCrossingBinnedByMinutes( tvec, vec, threshold = 5 ):
    """HIGH to LOW is crossing started 
    """
    state = 0
    crossingStarted = 0
    numCrossing = [ ]
    nCrossing = 0
    totalMinutes = 0

    startT = datetime.strptime( tvec[0], __fmt__ )
    binStartT = datetime.strptime( tvec[0], __fmt__ )
    binStopT = binStartT + timedelta( seconds = 60 )
    crossingStartTime = startT
    for i, v in enumerate(vec):
        try:
            t = datetime.strptime( tvec[i], __fmt__ )
        except Exception as e:
            print( 'Faiied to parse  %s' % tvec[i] )
            continue 

        if t >= binStopT:
            binStartT = binStopT 
            binStopT = binStartT + timedelta( seconds = 60 )
            totalMinutes += 1
            numCrossing.append( nCrossing )
            nCrossing = 0

        state = 0 if v < threshold else 1
        if crossingStarted and state == 1:
            # Crossing is over
            crossingStarted = False
            nCrossing += 1
        elif not crossingStarted and state == 0:
            crossingStarted = True
            crossingStartTime = t

    # print( 'Start time %s, End time %s' % ( startT, binStopT) )
    # print( 'Total minutes %d' % totalMinutes )
    return numCrossing



def count(  ):
    global args_
    data = pandas.read_csv( args_.infile, header=None, sep = ',' )
    data.dropna( )
    tvec = data.ix[:,0].values
    holes = [ ]
    # Arduino data
    pylab.figure( )
    # plot this data.
    pylab.plot( data.ix[:,10] )
    pylab.savefig( '%s_aduino.png' % args_.infile )
    print( 'Saved arduino data' )

    for i in range( len(data.columns) - 2 ):
        yvec = data.ix[:,i+1].values
        n = getCrossingBinnedByMinutes( tvec, yvec )
        print( 'Total crossing in this hole %f, avg %f, max %f' % (
                np.sum(n), np.mean( n ), np.max( n ) )
                )
        holes.append( n )
    return holes 


def plot( nCrossings ):
    global args_ 
    pylab.subplot(211)

    # sum crossing from all holes.
    allCrossings = np.sum( nCrossings, axis = 0 )
    tInHours = np.arange( 0, len( nCrossings[0] ) ) / 60.0

    nBlocks = 0
    tvec, yvec = [], []
    blockSizeInHours = 24
    for i, t in enumerate( tInHours ) :
        tvec.append( t - nBlocks * blockSizeInHours)
        yvec.append( allCrossings[ i ] )
        if t > (nBlocks + 1 ) * blockSizeInHours:
            nBlocks += 1
            pylab.plot( tvec, yvec, label = 'Day %d' % nBlocks )
            pylab.legend(loc='best', framealpha=0.4)
            tvec, yvec = [], []
            print( '%d day is done' % nBlocks )

    # Plot leftovers here
    pylab.plot( tvec, yvec, label = 'Day %d' % nBlocks )
    pylab.legend(loc='best', framealpha=0.4)
    pylab.subplot( 212 )
    pylab.tight_layout( )
    outfile = '%s_result.png' % args_.infile
    pylab.savefig( outfile )
    print( 'Image saved to %s' % outfile )

def main( ):
    global args_
    import argparse
    # Argument parser.
    description = '''Analyze bee data'''
    parser = argparse.ArgumentParser(description=description)
    class Args: pass 
    args_ = Args()
    parser.add_argument('--infile', '-i'
        , required = True
        , type = str
        , help = 'Data fle'
        )
    parser.parse_args(namespace=args_)
    nCrossHoles = count(  )
    plot( nCrossHoles )

if __name__ == '__main__':
    main()

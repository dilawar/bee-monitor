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
import datetime 
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

def getCrossingsPerMin( tvec, vec, threshold = 5 ):
    """HIGH to LOW is crossing started 
    """
    state = 0
    crossingStarted = 0
    numCrossing = [ ]
    crossingStartTime = 0
    nCrossing = 0
    startT = tvec[0]
    for i, v in enumerate(vec):
        t = tvec[i]
        if t - startT >= 60000:
            startT = t
            # print( 'minute is over' )
            numCrossing.append( nCrossing )
            nCrossing = 0

        state = 0 if v < threshold else 1
        if crossingStarted and state == 1:
            # Crossing is over
            crossingStarted = False
            if t - crossingStarted < 300:
                continue
            nCrossing += 1
        elif not crossingStarted and state == 0:
            crossingStarted = True
            crossingStartTime = t

    return numCrossing



def count(  ):
    global args_
    data = pandas.read_csv( args_.infile, header=None, sep = ',')
    data.dropna( )
    tvec = data.ix[:,0].values
    holes = [ ]
    for i in range( len(data.columns) - 2 ):
        yvec = data.ix[:,i+1].values
        n = getCrossingsPerMin( tvec, yvec )
        holes.append( n )
    return holes 


def plot( nCrossings ):
    global args_ 
    pylab.subplot(211)
    print( len( nCrossings ) )

    tInHours = np.arange( 0, len( nCrossings[0] ) ) / 60.0

    pylab.plot( tInHours, np.sum( nCrossings, axis = 0 ) )
    pylab.ylabel( 'Crossing per min' )
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
    parser.add_argument('--start-time', '-t'
        , required = True
        , help = 'When recording started eg. 0:0 for midnight, 13:00 for 1pm'
        )
    parser.parse_args(namespace=args_)
    nCrossHoles = count(  )
    plot( nCrossHoles )

if __name__ == '__main__':
    main()

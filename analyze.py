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
from collections import defaultdict

__fmt__ = "%Y-%m-%dT%H:%M:%S.%f"
__offset__ = 5.5            # IST +5:30
infile_ = None
ncols = 9

# how many crossing each hole
holes = defaultdict( list )

args_ = None

def get_count(  ):
    global holes
    global args_
    HIGH, LOW = 1, 0
    result = [ ]
    states = [ HIGH ] * ncols
    count = [ 0 ] * ncols
    checkpoint = 0.0
    nlines = 0
    crossingStartTime = 0
    crossingStarted = False
    with open( args_.infile, 'r' ) as f:
        for l in f:
            nlines += 1
            data = [ float(x) for x in filter(None, l.strip( ).split( ',' )) ]
            t = data[0]
            # time = starttime + datetime.timedelta( milliseconds = t )
            if t  / ( 1000 * 3600 ) >= checkpoint:
                print( '%.1f hours are done' % checkpoint )
                checkpoint += 1.0

            for i, v in enumerate(data[1:]):
                if v < 2:
                    curstate = LOW
                    if not crossingStarted:
                        crossingStarted = True
                        crossingStartTime = t
                else:
                    curstate = HIGH 

                # Compare with previous state. The crossing happens when there is
                # LOW to HIGH transition.
                if states[i] == LOW and curstate == HIGH:
                    if t - crossingStartTime > 100:
                        crossingStarted = False
                        count[i] += 1
                        c = ','.join( [ str(x) for x in count ] )
                        result.append( (t, count[:]) )
                        holes[i].append( t )

                states[i] = curstate 

    return result 

def renormalize( tvec, vec ):
    global infile_ 
    # resample time every second i.e. 1000 ms.
    newT = np.arange( 0, max( tvec ), 1000 )
    newval = np.interp( newT, tvec, vec )
    np.savetxt( '%s_out.csv' % infile_, np.vstack((newT, newval)).T, delimiter = ',' )
    print( 'Renormalized data is written to %s_out.csv' % infile_ )
    return newT * 1e-3, newval

def diff( vec ):
    result = np.diff( vec ) 
    return np.convolve( result, np.ones( 1000 ) / 1000 , 'same' )

def plot( result ):
    global infile_ 
    global holes
    import pylab
    pylab.style.use( 'ggplot' )
    tvec, countVec = [], []

    for t, vals in result:
        tvec.append( t )
        countVec.append( sum( vals ) )

    tvec, yvec = renormalize( tvec, countVec )

    # For plotting, make the time from midnight to midnight
    startT = [ int(x) for x in args_.start_time.split( ':' ) ]
    startTInSec = 60 * ( startT[0] * 60 + startT[1] )
    print( 'Starting time of experiment: %s' % startT )
    tvec += startTInSec 

    datadir = '%s_analysis' % args_.infile 
    if not os.path.isdir( datadir ):
        os.makedirs( datadir )

    pylab.subplot( 311 )
    # pylab.plot( tvec, yvec )
    ndays = 0
    tvec, rate = tvec[1:], diff( yvec ) * 60
    secsInDay = 24 * 3600
    i = 0
    while True:
        idx = np.where( (tvec > i * secsInDay ) & (tvec <= (i+1) * secsInDay )
                )[0]
        if len(idx) > 0:
            print( 'Plotting for day %d' % i )
            x = tvec[ idx ] - (i * secsInDay )
            y = rate[ idx ]
            np.savetxt( 
                    os.path.join( datadir, 'day_%d.csv' % (i+1) )
                    , np.vstack((x,y)).T 
                    , header = 'time,rate'
                    , delimiter = ','
                    )
            pylab.plot( x/3600, y, '.', label = 'day %d' % (i+1) )
            pylab.legend(loc='best', framealpha=0.4)
        else:
            break
        i += 1

    pylab.xlabel( 'Time (hour)' )
    pylab.ylabel( 'Rate of crossing per minute' )
    pylab.subplot( 312 )
    pylab.bar( range( ncols ), [ len(holes[hole]) for hole in holes ])
    pylab.xlabel( 'Hole index' )
    pylab.ylabel( 'Total crossing' )
    pylab.subplot( 313 )
    pylab.tight_layout( )
    outfile = os.path.join( datadir, 'result.png' )
    pylab.savefig( outfile )
    print( 'All data is saved to %s' % datadir )

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
    result = get_count(  )
    plot(  result )

if __name__ == '__main__':
    main()

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

def get_count( infile_ ):
    global holes
    HIGH, LOW = 1, 0
    result = [ ]
    states = [ HIGH ] * ncols
    count = [ 0 ] * ncols
    checkpoint = 0.0
    # outfile = open( '%s_out.txt' % infile_ , 'w' )
    nlines = 0
    with open( infile_, 'r' ) as f:
        for l in f:
            nlines += 1
            data = [ float(x) for x in filter(None, l.strip( ).split( ',' )) ]
            t = data[0]
            if t  / ( 1000 * 3600 ) >= checkpoint:
                print( '%f hours are done' % checkpoint )
                checkpoint += 1.0

            for i, v in enumerate(data[1:]):
                if v > 5:
                    curstate = HIGH
                else:
                    curstate = LOW 

                # Compare with previous state. The crossing happens when there is
                # LOW to HIGH transition.
                if states[i] == LOW and curstate == HIGH:
                    count[i] += 1
                    c = ','.join( [ str(x) for x in count ] )
                    # outfile.write( '%d,%s,%d\n' % (t, c, sum(count) ) )
                    result.append( (t, count[:]) )
                    holes[i].append( t )
                states[i] = curstate 
    # print( 'Results are written to %s' % outfile )
    # outfile.close( )
    return result 

def renormalize( tvec, vec ):
    global infile_ 
    newT = np.arange( 0, max( tvec ), 1000 ) * 1e-3
    newval = np.interp( newT, tvec, vec )
    np.savetxt( '%s_out.csv' % infile_, np.vstack((newT, newval)).T, delimiter = ',' )
    print( 'Renormalized data is written to %s_out.csv' % infile_ )
    return newT, newval

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

    pylab.subplot( 311 )
    # pylab.plot( tvec, yvec )
    pylab.plot( tvec[1:] / 3600, diff(yvec) * 60 )
    pylab.legend(loc='best', framealpha=0.4)
    pylab.xlabel( 'Time (hour)' )
    pylab.ylabel( 'Rate of crossing per minute' )
    pylab.subplot( 312 )
    pylab.bar( range( ncols ), [ len(holes[hole]) for hole in holes ])
    pylab.xlabel( 'Hole index' )
    pylab.ylabel( 'Total crossing' )
    pylab.subplot( 313 )
    pylab.tight_layout( )
    pylab.savefig( '%s.png' % infile_ )
    print( 'Saved to file %s.png' % infile_ )



def main( ):
    global infile_
    infile_ = sys.argv[1]
    result = get_count( infile_ )
    plot( result )

if __name__ == '__main__':
    main()

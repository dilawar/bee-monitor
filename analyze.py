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

__fmt__ = "%Y-%m-%dT%H:%M:%S.%f"
__offset__ = 5.5            # IST +5:30
infile_ = None

ncols = 9
def get_count( infile_ ):
    HIGH, LOW = 1, 0
    result = [ ]
    states = [ HIGH ] * ncols
    count = [ 0 ] * ncols
    checkpoint = 0.0
    outfile = open( '%s_out.txt' % infile_ , 'w' )
    with open( infile_, 'r' ) as f:
        for l in f:
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
                    c = ','.join( [ '%d' for x in count ] )
                    outfile.write( '%f,%s,%d' % (t, c, sum(count) ) )
                states[i] = curstate 
            result.append( count )
    print( 'Results are written to %s' % outfile )
    outfile.close( )
    return result 


def main( ):
    global infile_
    infile_ = sys.argv[1]
    get_count( infile_ )
    #plot( timestamp, count )

if __name__ == '__main__':
    main()

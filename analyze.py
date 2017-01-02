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
import matplotlib.pyplot as plt
import numpy as np
import pandas
import datetime 

plt.style.use( 'ggplot' )


__fmt__ = "%Y-%m-%dT%H:%M:%S.%f"
__offset__ = 5.5            # IST +5:30
infile_ = None

def get_count( timestamp, cols, thres = 5 ):
    HIGH, LOW = 1, 0
    result = [ ]
    states = [ HIGH ] * len( cols.columns )   # All states are high to begin with
    count = [ 0 ] * len( cols.columns )
    nEntries = len( timestamp )
    checkpoint = 0.0
    for i, t in enumerate( timestamp ):
        if t  / ( 1000 * 3600 ) >= checkpoint:
            print( '%f hours are done' % checkpoint )
            checkpoint += 1.0

        vec = cols.iloc[i,:].values
        for i, v in enumerate(vec):
            if v > 5:
                curstate = HIGH
            else:
                curstate = LOW 

            # Compare with previous state. The crossing happens when there is
            # LOW to HIGH transition.
            if states[i] == LOW and curstate == HIGH:
                count[i] += 1

            states[i] = curstate 
        result.append( count )
    return result 


def plot( timestamp, count ):
    global infile_
    #timestamp = pandas.to_datetime( timestamp ) #+ pandas.Timedelta('5.5 hours')
    outfile = '%s.png' % infile_

    gridSize = (3, 2)
    ax1 = plt.subplot2grid( gridSize, (0,0), colspan = 2 )
    ax2 = plt.subplot2grid( gridSize, (1,0), colspan = 2 )
    ax3 = plt.subplot2grid( gridSize, (2,0), colspan = 1 )
    ax4 = plt.subplot2grid( gridSize, (2,1), colspan = 1 )
    ax1.plot( timestamp, count, label = 'Count' )

    count1 = count.rolling( 1000 ).mean( )
    ax1.plot( timestamp, count1 )
    ax1.legend( loc = 'best' )

    ax2.plot( timestamp, count1.diff( ), label = 'Rate of in/out' )
    ax2.legend( loc = 'best' )



    plt.savefig( outfile )
    print( 'Saved to file %s' % outfile )


def main( ):
    global infile_
    infile_ = sys.argv[1]
    data = pandas.read_table( infile_, sep = ',', header = None )
    timestamp = data.iloc[:,0]
    result = get_count( timestamp, data.iloc[:,1:] )
    print result[-1]
    #plot( timestamp, count )

if __name__ == '__main__':
    main()

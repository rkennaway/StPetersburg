#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Based on the pseudocode in https://en.wikipedia.org/wiki/Mersenne_Twister. Generates uniformly distributed unsigned 32-bit integers in the range [0, 2^32 − 1] with the MT19937 algorithm.

Yaşar Arabacı <yasar11732 et gmail nokta com>

Modifications by [redacted] 2020 July.
1. Compatibility with Python 3:
    print requires parentheses on its arguments.
    xrange() is replaced by range().
2. Generates array of random values of any shape.
3. Renamed extract_number to rand_uint32.
4. New procedure rand_uint64 to generate 64-bit random integers.
5. New procedure rand_float64 to generate uniformly distributed float64 numbers
   in the range [0,1).
"""

import numpy as np

twisterLength = 624
seed = 0;

# Create a list to store the state of the generator
MT = [0 for i in range(twisterLength)]
index = 0

# To get last 32 bits
bitmask_1 = (2 ** 32) - 1

# To get 32. bit
bitmask_2 = 2 ** 31

# To get last 31 bits
bitmask_3 = (2 ** 31) - 1

# For regression testing of changes.
TESTNEW = True;

def initialize_generator(s):
    "Initialize the generator from a seed"
    global MT
    global bitmask_1
    global index
    global seed
    
    if s is None:
        from datetime import datetime
        now = datetime.now()
        s = now.microsecond

    seed = s
    MT[0] = seed
    for i in range(1,twisterLength):
        MT1 = MT[i-1]
        x1 = (1812433253 * MT1);
        x2 = ((MT[i-1] >> 30) + i);
        x12 = x1 ^ x2
        MT[i] = x12 & bitmask_1
    index = 0;
        

def rand_uint32( nn ):
    """
    Generate n 32-bit pseudorandom numbers.
    """
    global index
    global MT
    n = np.prod(nn)
    yy = np.zeros( n, dtype='uint32' )
    for i in range(n):
        if index == 0:
            generate_numbers()
        y = MT[index]
        y ^= y >> 11
        y ^= (y << 7) & 2636928640
        y ^= (y << 15) & 4022730752
        y ^= y >> 18
        yy[i] = y;
    
        index = (index + 1) % twisterLength
    
    yy = np.reshape(yy,nn)
    return yy
    
def rand_uint64( n ):
    """
    Generate n 64-bit pseudorandom numbers.
    """
    r1 = np.uint64( rand_uint32( n ) )
    r2 = np.uint64( rand_uint32( n ) ) << 32
    r = r1 | r2
    return(r)
    
def rand_real( n ):
    """
    Generate n uniformly distributed float64 numbers in the half-open interval [0,1).
    """
    r1 = rand_uint64( n );
    r = np.float64(r1)/(np.float64(1<<63)*2)
    return(r)
    

def generate_numbers():
    "Generate an array of twisterLength untempered numbers"
    global MT
    for i in range(twisterLength):
        y = (MT[i] & bitmask_2) + (MT[(i + 1 ) % twisterLength] & bitmask_3)
        MT[i] = MT[(i + 397) % twisterLength] ^ (y >> 1)
        if y % 2 != 0:
            MT[i] ^= 2567483615

def MTprint( fid ):
    fid.write( "twisterLength {:d}\n".format(twisterLength) )
    fid.write( "bitmask_1 {:d}\n".format(bitmask_1) )
    fid.write( "bitmask_2 {:d}\n".format(bitmask_2) )
    fid.write( "bitmask_3 {:d}\n".format(bitmask_3) )
    fid.write( "seed {:d}\n".format(seed) )
    fid.write( "index {:d}\n".format(index) )
    perRow = 7;
    for i in range(twisterLength):
        fid.write( " {:d}".format(MT[i]) )
        if (i % perRow)==perRow-1:
            fid.write( '\n' );
    if (twisterLength % perRow) != perRow-1:
        fid.write( '\n' );



if __name__ == "__main__":
#    from datetime import datetime
#    now = datetime.now()
    #initialize_generator(now.microsecond)
    initialize_generator(1234)
    x = rand_uint64(10000);
    f = open( "tgpy.txt","w")
    MTprint( f );
    f.close();
    
#    "Print 100 random numbers as an example"
#    xx = rand_uint32( 100 )
#    print( xx )
        
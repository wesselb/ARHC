#!/usr/bin/env python
"""
 ~/python/compression/copy/invert.py   by David MacKay and Christian Steinruecken 15.2.2016

 This "compression" algorithm simply reads in a 0/1 ascii file
 and writes out a file that is an inverted copy of the input :-)

 $ invert.py [N [verbose]] < file1 > file2
 Optional arguments:
    N       = number of bits to read
    verbose = whether to run tests

 This package uses the doctest module to test that its function 'invert' is functioning correctly.
"""

import sys

def invert(c):
    """
    This documentation can be automatically tested by the doctest package
    >>> invert("1")
    '0'
    >>> invert("0")
    '1'
    """
    return str(1-int(c)) ;# this ought to have error checking :-)

def encode(N,instream,outstream,verbose):
    n=0
    while n<N :
        c = instream.read(1)
        if len(c) == 0:
            sys.stderr.write("ERROR: instream ended before was able to read "+str(N)+" symbols; n="+str(n)+"\n")
            return -1
        else:
            n += 1
            outstream.write(invert(c))
            pass
        pass
    if(verbose):
        sys.stderr.write("Received n="+str(n)+" symbols from input stream\n")
        pass
    return 0

def test():
    import doctest
    verbose=1
    if(verbose):
        sys.stderr.write("Sending self-test results to stdout\n")
        doctest.testmod(None,None,None,True)
    else:
        doctest.testmod()
        pass
    pass

if __name__ == '__main__':
    N=10           ;#     default parameter setting - number of characters to read and write
    verbose=1      ;#     default parameter setting - whether to be verbose
    if(len(sys.argv)>1):
        N=int(sys.argv[1])
        pass
    if(len(sys.argv)>2):
        verbose=int(sys.argv[2])
        pass
    if(verbose):
        test()
    encode(N,   sys.stdin , sys.stdout , verbose )
    pass


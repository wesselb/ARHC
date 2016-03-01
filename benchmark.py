#!/usr/bin/env python

import math
import os
import sys
from subprocess import Popen, PIPE
from random import random


class Test:
    def __init__(self, bits):
        self.bits = bits
        
    def run(self, args=[]):
        pComp = Popen(['./squash.py'] + args, stdin=PIPE, stdout=PIPE)
        pDecomp = Popen(['./squash.py', '--decompress'] + args, stdin=PIPE, stdout=PIPE)
        pComp.stdin.write(self.bits)
        outComp = pComp.stdout.read()
        pDecomp.stdin.write(outComp)
        outDecomp = pDecomp.stdout.read()
        pComp.wait()
        pDecomp.wait()
        self.outComp = outComp
        self.outDecomp = outDecomp
        self.ensureConsistency()

    def ensureConsistency(self):
        if self.outDecomp != self.bits:
            exit('Compressor not functioning properly')

    def getCompressedLength(self):
        return len(self.outComp)


def main():
    with open('benchmark.txt', 'r') as f:
        test = Test(f.read().strip())
    # test = Test('11000000001000000000000000000000100000100000000000000100001000000000100000000000001000000000100010000000010000000100001000000000000000001100000000000100000000000101000000000000000000001010000000000000')

    test.run()#['--N', '200'])
    sys.stderr.write('Static:   {:.0f}\n'.format(test.getCompressedLength()))
    test.run(['--adaptive', '--alpha0', '0.2', '--alpha1', '0.2'])
    sys.stderr.write('Adaptive: {:.0f}\n'.format(test.getCompressedLength()))



if __name__ == '__main__':
    main()

#!/usr/bin/env python

import math
import os
import sys
from subprocess import Popen, PIPE
from random import random

def mean(x):
    return sum(x) / len(x)

def std(x):
    return math.sqrt(mean(map(lambda y: (y - mean(x)) ** 2, x)))

class Test:
    def __init__(self, bits):
        self.bits = bits
        
    def run(self, args=[]):
        pComp = Popen(['./arhc.py'] + args, stdin=PIPE, stdout=PIPE)
        pDecomp = Popen(['./arhc.py', '--decompress'] + args, stdin=PIPE, stdout=PIPE)
        pComp.stdin.write(self.bits)
        outComp = pComp.stdout.read()
        outComp2 = pComp.stdout.read()
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

def bitString(N, p):
    return ''.join(map(lambda x: '0' if x > p else '1', [random() for _ in range(N)]))

def main():
    N = 10000
    p = 0.01
    H = -(p * math.log(p) + (1 - p) * math.log(1 - p)) / math.log(2)
    lenOpt = H * N
    print('Optimal expected length: {:.0f}'.format(lenOpt))

    lensStatic = []
    lensAdapt = []

    for i in range(50):
        print('Iteration {}/{}'.format(i + 1, 10))
        test = Test(bitString(N, p))
        test.run([])
        lensStatic.append(test.getCompressedLength())
        test.run(['--adaptive'])
        lensAdapt.append(test.getCompressedLength())
        print('Static length: {:.0f}, adaptive length: {:.0f}'.format(lensStatic[-1], lensAdapt[-1]))

    print('Static average length:  {:.0f} +- {:.0f}'.format(mean(lensStatic), std(lensStatic)))
    print('Adapt average length:   {:.0f} +- {:.0f}'.format(mean(lensAdapt), std(lensAdapt)))

if __name__ == '__main__':
    main()

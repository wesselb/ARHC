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
        pDecomp = Popen(
            ['./squash.py', '--decompress'] + args, stdin=PIPE, stdout=PIPE)
        pComp.stdin.write(self.bits)
        outComp = pComp.stdout.read()
        pDecomp.stdin.write(outComp)
        outDecomp = pDecomp.stdout.read()
        pComp.wait()
        pDecomp.wait()
        self.ensureConsistency(outDecomp)

    def ensureConsistency(self, outDecomp):
        if outDecomp != self.bits:
            exit('Decompressed output not consistent with input')


def bitString(N, p):
    return ''.join(map(lambda x: '0' if x > p else '1',
                       [random() for _ in range(N)]))


def main():
    Nps = [(10000, 0.1), (500, 0.1)]

    for N, p in Nps:
        test = Test(bitString(N, p))
        test.run(['--N', str(N), '--prob1', str(p)])
        test.run(['--adaptive', '--N', str(N), '--prob1', str(p)])

    print 'Verified'

if __name__ == '__main__':
    main()

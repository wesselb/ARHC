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
        pComp = Popen(['./squash'] + args, stdin=PIPE, stdout=PIPE)
        pDecomp = Popen(['./unsquash'] + args, stdin=PIPE, stdout=PIPE)
        pComp.stdin.write(self.bits)
        outComp = pComp.stdout.read()
        pDecomp.stdin.write(outComp)
        outDecomp = pDecomp.stdout.read()
        pComp.wait()
        pDecomp.wait()
        self.ensureConsistency(outDecomp)
        return outComp

    def ensureConsistency(self, outDecomp):
        if outDecomp != self.bits:
            exit('Decompressed output not consistent with input')


def bitString(N, p):
    return ''.join(map(lambda x: '0' if x > p else '1',
                       [random() for _ in range(N)]))


def main():
    N = 10000
    p = 0.01

    with open('tests/benchmark.txt', 'r') as f:
        inp = f.read().strip()

    test = Test(inp)
    test.run(['--prob1', str(p), '--N', str(N)])
    test = Test(inp)
    test.run(['--prob1', str(p), '--N', str(N), '--adaptive'])

    sys.stderr.write('OK\n')


if __name__ == '__main__':
    main()

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
    runs = 500

    H = -(p * math.log(p) + (1 - p) * math.log(1 - p))/math.log(2)
    lenOpt = H * N
    lens = []

    def mean(xs): return sum(map(float, xs)) / len(xs)
    def std(x): return math.sqrt(mean(map(lambda y: (y - mean(x)) ** 2, x)))

    for i in range(runs):
        sys.stderr.write('Run {}/{}\n'.format(i + 1, runs))
        test = Test(bitString(N, p))
        lens.append(len(test.run(['--prob1', str(p)])))

    sys.stderr.write('Length:   {:.2f} +- {:.2f}\n'.format(mean(lens), std(lens)))
    sys.stderr.write('Overhead: {:.2f} +- {:.2f}\n'.format(mean(map(lambda x: x - lenOpt, lens)), std(lens)))


if __name__ == '__main__':
    main()

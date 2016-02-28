#!/usr/bin/env python

import math
import os
import sys
import time
import fcntl
from fcntl import fcntl , F_GETFL, F_SETFL
from subprocess import Popen, PIPE
from os import O_NONBLOCK
from random import random

class Main:
    # IMPORTANT!!!
    writeTimeMs = 10

    H = -(0.99 * math.log(0.99) + 0.01 * math.log(0.01)) / math.log(2)
    lenOpt = math.ceil(H * 10000)

    def nonBlock(self, stream):
        flags = fcntl(stream, F_GETFL)
        fcntl(stream, F_SETFL, flags | O_NONBLOCK)

    def read(self, stream):
        out = ''
        while True:
            try:
                out += os.read(stream.fileno(), 1)
            except OSError:
                # OS throws exception if no more data is available
                break
        return out

    def write(self, stream, string):
        stream.write(string)
        time.sleep(self.writeTimeMs / 1000.0)

    def run(self, args, bits, inputFn):
        fileIn = open(inputFn, 'r')
        pDecomp = Popen(['./arhc.py', '--decompress'] + args, stdin=PIPE, stdout=PIPE)
        pComp = Popen(['./arhc.py'] + args, stdin=PIPE, stdout=PIPE)

        # Make pipes non-blocking
        self.nonBlock(pComp.stdin)
        self.nonBlock(pComp.stdout)
        self.nonBlock(pDecomp.stdin)
        self.nonBlock(pDecomp.stdout)

        track = Track()
        for i in range(bits):
            sys.stderr.write('Bit {}/{}\n'.format(i + 1, bits))
            bitIn = fileIn.read(1)
            self.write(pComp.stdin, bitIn)
            compOut = self.read(pComp.stdout)
            self.write(pDecomp.stdin, compOut)
            decompOut = self.read(pDecomp.stdout)
            track.track(bitIn, compOut, decompOut)

        pComp.kill()
        pDecomp.kill()

        return track

class Track:
    i = 0
    bitInAccum = ''
    bitInAccumST = ''
    compOutAccum = ''
    symbol = False
    tab = ''
    rats = []
    ratsST = []
    decompBits = 0

    def __init__(self):
        self.rats = []
        self.ratsST = []

    def track(self, bitIn, compOut, decompOut):
        self.bitInAccum += bitIn
        self.bitInAccumST += bitIn
        self.compOutAccum += compOut
        self.decompBits += len(decompOut)
        symbol = compOut != ''
        self.table(bitIn, compOut, decompOut)
        self.ensureConsistency(symbol, decompOut)
        self.ratioST(symbol, compOut)
        self.ratio(symbol)
        self.next(symbol)

    def next(self, symbol):
        if symbol:
            self.bitInAccumST = ''
        self.i += 1

    def table(self, bitIn, compOut, decompOut):
        if self.i < 60:
            self.tab += '\\code{{\\scriptsize {:s}}} & \\code{{\\scriptsize {:s}}} & \\code{{\\scriptsize {:s}}} \\\\ \n'.format(
                    bitIn, compOut, decompOut)

    def getTable(self):
        return self.tab

    def ensureConsistency(self, symbol, decompOut):
        if symbol and self.bitInAccumST != decompOut:
            sys.stderr.write('!! Compressor and decompressor inconsistent\n')

    def ratio(self, symbol):
        if symbol:
            self.rats += [(self.i, 1 - float(len(self.compOutAccum))/len(self.bitInAccum))]

    def ratioST(self, symbol, compOut):
        if symbol:
            self.ratsST += [(self.i, 1 - float(len(compOut))/len(self.bitInAccumST))]

    def getRatioST(self):
        return 'ratiosST = [\n    ' + '    '.join(map(lambda x: '{} {}\n'.format(*x), self.ratsST)) + '];\n'

    def getRatio(self):
        return 'ratios = [\n    ' + '    '.join(map(lambda x: '{} {}\n'.format(*x), self.rats)) + '];\n'



if __name__ == '__main__':
    main = Main()

    N = 2000
    p = 0.01

    for i in range(100):
        f = open('temp.txt', 'w')
        f.write(''.join(map(lambda x: '0' if x > p else '1', [random() for _ in range(N)])))
        f.close()

        track = main.run(['--adaptive', '--N', str(N)], N, 'temp.txt')
        with open('data/adaptive_tab' + str(i) + '.tex', 'w') as f:
            f.write(track.getTable())
        with open('data/adaptive_ratios' + str(i) + '.m', 'w') as f:
            f.write(track.getRatio())
        with open('data/adaptive_ratiosST' + str(i) + '.m', 'w') as f:
            f.write(track.getRatioST())

        track = main.run(['--N', str(N)], N, 'temp.txt')
        with open('data/static_tab' + str(i) + '.tex', 'w') as f:
            f.write(track.getTable())
        with open('data/static_ratios' + str(i) + '.m', 'w') as f:
            f.write(track.getRatio())
        with open('data/static_ratiosST' + str(i) + '.m', 'w') as f:
            f.write(track.getRatioST())


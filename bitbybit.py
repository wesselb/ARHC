#!/usr/bin/env python

import math
import os
import sys
import time
import fcntl
import textwrap
from fcntl import fcntl, F_GETFL, F_SETFL
from subprocess import Popen, PIPE
from os import O_NONBLOCK
from random import random


class Test:
    writeTimeMs = 60

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

    def run(self, args):
        bitsCopy = list(self.bits)
        pDecomp = Popen(
            ['./squash.py', '--decompress'] + args, stdin=PIPE, stdout=PIPE)
        pComp = Popen(['./squash.py'] + args, stdin=PIPE, stdout=PIPE)

        # Make pipes non-blocking
        self.nonBlock(pComp.stdin)
        self.nonBlock(pComp.stdout)
        self.nonBlock(pDecomp.stdin)
        self.nonBlock(pDecomp.stdout)

        track = Track()
        for i in range(len(self.bits)):
            sys.stderr.write('{} '.format(i + 1))
            bitIn = bitsCopy.pop(0)
            self.write(pComp.stdin, bitIn)
            compOut = self.read(pComp.stdout)
            self.write(pDecomp.stdin, compOut)
            decompOut = self.read(pDecomp.stdout)
            track.track(bitIn, compOut, decompOut)
        sys.stderr.write('\n')

        pComp.stdin.close()
        pComp.stdout.close()
        pDecomp.stdin.close()
        pDecomp.stdout.close()

        pComp.kill()
        pDecomp.kill()

        return track

    def setBits(self, bits):
        self.bits = bits


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
        if len(decompOut) > 25:
            decompOut = decompOut[:25]
            dots = '$\\cdots$'
        else:
            dots = ''
        self.tab += '\\code{{\\scriptsize {:s}}} &' \
                    ' \\code{{\\scriptsize {:s}}} &' \
                    ' \\code{{\\scriptsize {:s}{}}}' \
                    ' \\\\ \n'.format(bitIn, compOut, decompOut, dots)

    def getTable(self):
        return self.tab

    def ensureConsistency(self, symbol, decompOut):
        if symbol and self.bitInAccumST != decompOut:
            sys.stderr.write('!! Compressor and decompressor inconsistent\n')

    def ratio(self, symbol):
        if symbol:
            self.rats += [(self.i, 1 - float(len(self.compOutAccum)) /
                           len(self.bitInAccum))]

    def ratioST(self, symbol, compOut):
        if symbol:
            self.ratsST += [(self.i, 1 - float(len(compOut)) /
                             len(self.bitInAccumST))]

    def getRatioST(self):
        return 'ratiosST = [\n    ' + '    '.join(
            map(lambda x: '{} {}\n'.format(*x), self.ratsST)) + '];\n'

    def getRatio(self):
        return 'ratios = [\n    ' + '    '.join(
            map(lambda x: '{} {}\n'.format(*x), self.rats)) + '];\n'


def bitString(N, p):
    return ''.join(map(lambda x: '0' if x > p else '1',
                       [random() for _ in range(N)]))


if __name__ == '__main__':
    p = 0.01
    H = -(p * math.log(p) + (1 - p) * math.log(1 - p))/math.log(2)
    test = Test()

    execTables = False
    execComparison1 = False
    execComparison1Mismatch = False
    execPriors1 = True

    if execTables:
        sys.stderr.write('Tables\n')
        N = 80
        test.setBits(
            '0100000000000000000000000000000010000000000000000000000000000000000'
            '0000000000100000000000000000000000100000000000000010000000000000000'
            '0000000000000000000000000000000000000000000000'[:N])
        track = test.run(['--adaptive', '--N', str(N), '--alpha0', '0.5',
                          '--alpha1', '0.5'])
        lenAdapt = len(track.compOutAccum)
        with open('data/tab_adaptive.tex', 'w') as f:
            f.write(track.getTable())
        track = test.run(['--N', str(N)])
        lenStat = len(track.compOutAccum)
        with open('data/tab_static.tex', 'w') as f:
            f.write(track.getTable())

        print textwrap.dedent('''
            Input length:    {}
            Static length:   {}
            Adaptive length: {}
            Optimal length:  {}
            ''').format(N, lenStat, lenAdapt, int(math.ceil(H*N)))

    if execComparison1:
        N = 200
        p = 0.1
        runs = 200

        for i in range(runs):
            sys.stderr.write('Run {}/{}\n'.format(i + 1, runs))
            test.setBits(bitString(N, p))

            track = test.run(['--adaptive', '--N', str(N), '--prob1', str(p)])
            with open('data/adaptive_ratios' + str(i) + '.m', 'w') as f:
                f.write(track.getRatio())
            with open('data/adaptive_ratiosST' + str(i) + '.m', 'w') as f:
                f.write(track.getRatioST())

            track = test.run(['--N', str(N), '--prob1', str(p)])
            with open('data/static_ratios' + str(i) + '.m', 'w') as f:
                f.write(track.getRatio())
            with open('data/static_ratiosST' + str(i) + '.m', 'w') as f:
                f.write(track.getRatioST())

    if execComparison1Mismatch:
        N = 200
        p = 0.1
        pActual = 0.01
        runs = 200

        for i in range(runs):
            sys.stderr.write('Run {}/{}\n'.format(i + 1, runs))
            test.setBits(bitString(N, pActual))

            track = test.run(
                ['--adaptive', '--N', str(N), '--prob1', str(p), '--alpha0', '0.1', '--alpha1', '0.1'])
            with open('data/adaptive_ratios_mismatch' + str(i) + '.m', 'w') as f:
                f.write(track.getRatio())
            with open('data/adaptive_ratiosST_mismatch' + str(i) + '.m', 'w') as f:
                f.write(track.getRatioST())

            track = test.run(['--N', str(N), '--prob1', str(p)])
            with open('data/static_ratios_mismatch' + str(i) + '.m', 'w') as f:
                f.write(track.getRatio())
            with open('data/static_ratiosST_mismatch' + str(i) + '.m', 'w') as f:
                f.write(track.getRatioST())

    if execPriors1:
        N = 200
        p = 0.1
        alphas = [(0.1, 0.1), (1.0, 1.0), (5.0, 5.0)]
        runs = 50

        for j, (alpha0, alpha1) in enumerate(alphas):
            if j == 0:
                continue
            for i in range(runs):
                sys.stderr.write('Prior {}/{}, run {}/{}\n'.format(
                    j + 1, len(alphas), i + 1, runs))
                test.setBits(bitString(N, p))
                track = test.run(['--adaptive', '--N', str(N), '--prob1',
                                  str(p), '--alpha0', str(alpha0),
                                  '--alpha1', str(alpha1)])

                with open('data/prior' + str(j) + '_run' + str(i) + '.m', 'w') as f:
                    f.write(track.getRatio())

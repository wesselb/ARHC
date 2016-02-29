#!/usr/bin/env python

import math
import os
import sys
from subprocess import Popen, PIPE
from random import random

def mean(x):
    return sum(x) / float(len(x))

def std(x):
    return math.sqrt(mean(map(lambda y: (y - mean(x)) ** 2, x)))

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

def runGroupTest(numRuns, N, p, H):
    lensStatic = []
    lensAdapt = []

    for i in range(numRuns):
        print('Iteration {}/{}'.format(i + 1, numRuns))
        test = Test(bitString(N, p))
        test.run(['--N', str(N)])
        lensStatic.append(test.getCompressedLength())
        test.run(['--adaptive', '--N', str(N)])
        lensAdapt.append(test.getCompressedLength())
        print('Static length: {:.0f}, adaptive length: {:.0f}'.format(lensStatic[-1], lensAdapt[-1]))

    print('Static average length:  {:.0f} +- {:.0f}'.format(mean(lensStatic), std(lensStatic)))
    print('Adapt average length:   {:.0f} +- {:.0f}'.format(mean(lensAdapt), std(lensAdapt)))

    def toRat(ls): return [1 - float(l)/(N * H) for l in ls]
    meanRatStat = mean(toRat(lensStatic))
    stdRatStat = std(toRat(lensStatic))
    meanRatAdapt = mean(toRat(lensAdapt))
    stdRatAdapt = std(toRat(lensAdapt))

    return mean(toRat(lensStatic)), std(toRat(lensStatic)), mean(toRat(lensAdapt)), std(toRat(lensAdapt))
    return mean


def writeMatlabFile(varName, List, filename):
    if os.path.isfile(filename):
        f = open(filename, 'a')
    else:
        f = open(filename, 'w')
    stringToWrite = varName + " = " + str(List) + ";\n"
    f.write(stringToWrite)
    f.close()


def bitString(N, p):
    return ''.join(map(lambda x: '0' if x > p else '1', [random() for _ in range(N)]))


def main():
    p = 0.01
    bitLengths = map(int, [1e3, 2e3, 3e3, 4e3, 5e3, 6e3, 7e3, 8e3, 9e3, 10e3])
    numRuns = 50

    meanStaticList = []
    stdStaticList = []
    meanAdaptList = []
    stdAdaptList = []

    for i, N in enumerate(bitLengths):
        sys.stderr.write('Experiment {}/{}\n'.format(i + 1, len(bitLengths)))
        H = -(p * math.log(p) + (1 - p) * math.log(1 - p)) / math.log(2)
        meanStatic, stdStatic, meanAdapt, stdAdapt = runGroupTest(numRuns, N, p, H)
        meanStaticList.append(meanStatic)
        stdStaticList.append(stdStatic)
        meanAdaptList.append(meanAdapt)
        stdAdaptList.append(stdAdapt)

    filename = "data/performance1.m"
    if os.path.isfile(filename):
        os.remove(filename)
    writeMatlabFile("bitLengths", bitLengths, filename)
    writeMatlabFile("meanStaticList", meanStaticList, filename)
    writeMatlabFile("stdStaticList", stdStaticList, filename)
    writeMatlabFile("meanAdaptList", meanAdaptList, filename)
    writeMatlabFile("stdAdaptList", stdAdaptList, filename)



if __name__ == '__main__':
    main()

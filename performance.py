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

def runGroupTest(numRuns, N, p):
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
    return mean(lensStatic), std(lensStatic), mean(lensAdapt), std(lensAdapt)


def writeMatlabFile(varName, List, filename):
    if os.path.isfile(filename):
        f = open(filename, 'a')
    else:
        f = open(filename, 'w')
    stringToWtite = varName + " = " + str(List) + ";\n"
    f.write(stringToWtite)
    f.close()


def bitString(N, p):
    return ''.join(map(lambda x: '0' if x > p else '1', [random() for _ in range(N)]))


def main():
    p = 0.01
    bitlenghts = [100, 250,  500, 1000, 2500, 5000, 7500, 10000]
    numRuns = 1000

    meanStaticList = []
    stdStaticList = []
    meanAdaptList = []
    stdAdaptList = []
    entropyList  = []
    expectedLengthList = []


    for N in bitlenghts:
        H = -(p * math.log(p) + (1 - p) * math.log(1 - p)) / math.log(2)
        lenOpt = H * N
        print('Optimal expected length: {:.0f}'.format(lenOpt))
        meanStatic, stdStatic, meanAdapt, stdAdapt = runGroupTest(numRuns, N, p)
        meanStaticList.append(meanStatic)
        stdStaticList.append(stdStatic)
        meanAdaptList.append(meanAdapt)
        stdAdaptList.append(stdAdapt)
        entropyList.append(H)
        expectedLengthList.append(lenOpt)

    filename = "results.m"
    if os.path.isfile(filename):
        os.remove(filename)
    writeMatlabFile("bitlenghts", bitlenghts, filename)
    writeMatlabFile("meanStaticList", meanStaticList, filename)
    writeMatlabFile("stdStaticList", stdStaticList, filename)
    writeMatlabFile("meanAdaptList", meanAdaptList, filename)
    writeMatlabFile("stdAdaptList", stdAdaptList, filename)
    writeMatlabFile("entropyList", entropyList, filename)
    writeMatlabFile("expectedLengthList", expectedLengthList, filename)



if __name__ == '__main__':
    main()

#!/usr/bin/env python

import sys
import math
import textwrap
import time


class Word:
    def __init__(self, string, prob):
        self.prob = prob
        self.string = string

    def getProb(self):
        return self.prob

    def getEncoding(self, encoding):
        return [(self.string, encoding)]

    def decode(self, stream):
        return self.string


class MergedWord:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def getProb(self):
        return self.left.getProb() + self.right.getProb()

    def getEncoding(self, prefix=''):
        return self.left.getEncoding(prefix + '0') + self.right.getEncoding(prefix + '1')

    def decode(self, stream):
        if stream.read() == '0':
            return self.left.decode(stream)
        else:
            return self.right.decode(stream)


def pd(object):
    sys.stderr.write('DEBUG: ' + str(object) + '\n')

class Huffman:
    def __init__(self, words):
        self.words = filter(lambda word: word.getProb() > 0, words)
        self.build()

    def build(self):
        while len(self.words) > 1:
            self.mergeTwoLowestProbWords()
        self.encoding = dict(self.words[0].getEncoding())

    def mergeTwoLowestProbWords(self):
        self.words.sort(key=lambda word: word.getProb())
        self.words.insert(0, MergedWord(self.words.pop(0), self.words.pop(0)))

    def encode(self, stream):
        word = ''
        while stream.areBitsLeftToRead() and not (word in self.encoding):
            word += stream.read()
        return self.encoding[word] if word in self.encoding else self.encoding['EOT']

    def decode(self, stream):
        return self.words[0].decode(stream)


class AdaptiveProbability:
    count0 = 0
    count1 = 0

    def __init__(self, alpha0, alpha1):
        self.alpha0 = alpha0
        self.alpha1 = alpha1

    def observe(self, string):
        observed1 = sum(map(int, string))
        self.count0 += len(string) - observed1
        self.count1 += observed1

    def getPredictive1(self):
        return (self.count1 + self.alpha1) / (self.count0 + self.alpha0 + self.count1 + self.alpha1)

    def getRunLength(self):
        return int(round(math.log(0.5) / math.log(1 - self.getPredictive1())))


class ConstantProbability:
    def __init__(self, prob1, runLength):
        self.prob1 = prob1
        self.runLength = runLength

    def observe(self, string):
        pass

    def getPredictive1(self):
        return self.prob1

    def getRunLength(self):
        return self.runLength


class ARHC:
    def __init__(self, inStream, outStream, N, prob1):
        self.prob1 = prob1
        self.N = N
        self.inStream = Stream(inStream, N)
        self.outStream = Stream(outStream, N)
        self.buildHuffman(N)

    def buildHuffman(self, bitsLeft):
        prob1 = self.prob1.getPredictive1()
        runLength = min(bitsLeft, self.prob1.getRunLength())
        self.words = [Word(
            '0' * runLength,
            pow(1 - prob1, runLength)
            )]
        for i in range(runLength + 1):
            self.words.append(Word(
                '0' * i + '1',
                pow(1 - prob1, i) * prob1
                ))
        self.huff = Huffman(self.words)

    def compress(self):
        self.inStream.attachRead(self.prob1.observe)
        while True:
            self.outStream.write(self.huff.encode(self.inStream))
            if self.inStream.areBitsLeftToRead():
                self.buildHuffman(self.inStream.bitsLeftToRead())
            else:
                break

    def decompress(self):
        self.outStream.attachWrite(self.prob1.observe)
        word = self.huff.decode(self.inStream)
        while True:
            self.outStream.write(word)
            if self.outStream.areBitsLeftToWrite():
                self.buildHuffman(self.outStream.bitsLeftToWrite())
                word = self.huff.decode(self.inStream)
            else:
                break
        self.outStream.write('0' * self.outStream.bitsLeftToWrite())


class Stream:
    bitsRead = 0
    bitsWritten = 0
    observerRead = lambda self, x: None
    observerWrite = lambda self, x: None

    def __init__(self, stream, N):
        self.stream = stream
        self.N = N

    def read(self, num=1):
        self.bitsRead += num
        contents = self.stream.read(num)
        self.observerRead(contents)
        return contents

    def write(self, string):
        self.bitsWritten += len(string)
        self.observerWrite(string)
        self.stream.write(string)
        self.stream.flush()

    def bitsLeftToRead(self):
        return self.N - self.bitsRead

    def bitsLeftToWrite(self):
        return self.N - self.bitsWritten

    def areBitsLeftToRead(self):
        return self.bitsLeftToRead() > 0

    def areBitsLeftToWrite(self):
        return self.bitsLeftToWrite() > 0

    def attachRead(self, observer):
        self.observerRead = observer

    def attachWrite(self, observer):
        self.observerWrite = observer

    
class Main:
    usage = textwrap.dedent('''
    Adaptive Run-length Huffman Compressor (ARHC)
    James Requeima and Wessel Bruinsma

    Usage:
        arhc.py < inputFile > outputFile

    Flags:
        --decompress         Decompress inputFile
        --N length           Length of inputFile, default 10000
        --help               Show this information

        Static compression
        --prob1 value        Probability of one, default 0.01
        --runLength value    Run-length, default 69*2

        Adaptive compression
        --adaptive           Use adaptive compression scheme
        --alpha0 value       Concentration parameter associated with probability of zero, default 1.0
        --alpha1 value       Concentration parameter associated with probability of one, default 0.1

    Details:
        Compresses by default. Uses static compression scheme by default.
    ''')

    args = {
        'decompress': False,
        'N': 10000,
        'adaptive': False,
        'alpha0': 1.0,
        'alpha1': 0.1,
        'prob1': 0.01,
        'runLength': 69*2,
        'help': False
    }

    def error(self, message):
        sys.stderr.write(message[0].capitalize() + message[1:] + '\n')
        sys.stderr.write('Use "arhc.py --help" to view more information.\n')
        exit()

    def parseArguments(self):
        iterator = iter(sys.argv)
        next(iterator) # Skip file name
        for arg in iterator:
            if len(arg) < 2 or arg[:2] != '--':
                self.error('syntax error "{}"'.format(arg))
            else:
                self.parseArgument(arg[2:], lambda: next(iterator))

    def parseArgument(self, arg, getValue):
        if arg in self.args:
            if type(self.args[arg]) == bool:
                self.args[arg] = True
            else:
                self.args[arg] = type(self.args[arg])(getValue())
        else:
            self.error('unknown argument "--{}"'. format(arg))

    def run(self):
        if self.args['help']:
            sys.stdout.write(self.usage)
        else:
            if self.args['adaptive']:
                prob1 = AdaptiveProbability(self.args['alpha0'], self.args['alpha1'])
            else:
                prob1 = ConstantProbability(self.args['prob1'], self.args['runLength'])
            arhc = ARHC(sys.stdin, sys.stdout, self.args['N'], prob1)
            if not self.args['decompress']:
                arhc.compress()
            else:
                arhc.decompress()


if __name__ == '__main__':
    main = Main()
    main.parseArguments()
    main.run()
    time.sleep(0.01) # Keep process alive for just another bit

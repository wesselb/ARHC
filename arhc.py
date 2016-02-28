#!/usr/bin/env python

import sys
import math
import textwrap
import time


class Leaf:
    """
    Encapsulation of a symbol in a symbol code. When used in conjunction with Node it acts as the leaf of a
    binary tree.

    Args:
        symbol (string): Representation of the symbol as a string.
        prob (float): Probability of the symbol.
    """
    def __init__(self, symbol, prob):
        self.prob = prob
        self.symbol = symbol

    def getProb(self):
        return self.prob

    def getEncoding(self, encoding):
        return [(self.symbol, encoding)]

    def decode(self, stream):
        return self.symbol


class Node:
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


class Huffman:
    def __init__(self, words):
        self.build(words)

    def build(self, words):
        while len(words) > 1:
            self.mergeTwoLowestProbWords(words)
        self.root = words[0]
        self.encoding = dict(self.root.getEncoding())

    def mergeTwoLowestProbWords(self, words):
        words.sort(key=lambda word: word.getProb())
        words.insert(0, Node(words.pop(0), words.pop(0)))

    def encode(self, stream):
        symbol = ''
        while not (symbol in self.encoding):
            symbol += stream.read()
        return self.encoding[symbol]

    def decode(self, stream):
        return self.root.decode(stream)


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


class ConstantProbability:
    def __init__(self, prob1):
        self.prob1 = prob1

    def observe(self, string):
        pass

    def getPredictive1(self):
        return self.prob1


class ARHC:
    def __init__(self, prob1):
        self.prob1 = prob1

    def calculateOptimalRunLength(self):
        return int(round(math.log(0.5) / math.log(1 - self.prob1.getPredictive1())))

    def buildWords(self, runLength):
        words = [Leaf('0' * runLength, pow(1 - self.prob1.getPredictive1(), runLength))]
        for i in range(runLength + 1):
            words.append(Leaf('0' * i + '1', pow(1 - self.prob1.getPredictive1(), i) * self.prob1.getPredictive1()))
        return words

    def buildHuffman(self, bitsLeft):
        runLength = min(bitsLeft, self.calculateOptimalRunLength())
        words = self.buildWords(runLength)
        self.huffman = Huffman(words)

    def compress(self, inStream, outStream):
        inStream.observeRead(self.prob1.observe)
        while inStream.bitsLeftToRead() > 0:
            self.buildHuffman(inStream.bitsLeftToRead())
            outStream.write(self.huffman.encode(inStream))

    def decompress(self, inStream, outStream):
        outStream.observeWrite(self.prob1.observe)
        while outStream.bitsLeftToWrite() > 0:
            self.buildHuffman(outStream.bitsLeftToWrite())
            outStream.write(self.huffman.decode(inStream))


class Stream:
    bitsRead = 0
    bitsWritten = 0
    observerRead = lambda self, x: None
    observerWrite = lambda self, x: None

    def __init__(self, stream, N):
        self.stream = stream
        self.N = N

    def read(self, num=1):
        contents = self.stream.read(num)
        self.bitsRead += len(contents)
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

    def observeRead(self, observer):
        self.observerRead = observer

    def observeWrite(self, observer):
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

        Adaptive compression
        --adaptive           Use adaptive compression scheme
        --alpha0 value       Concentration parameter associated with probability of zero, default 1.0
        --alpha1 value       Concentration parameter associated with probability of one, default 0.1

    Details:
        Compresses by default. Uses static compression scheme by default.
    ''')

    arguments = {
        'decompress': False,
        'N': 10000,
        'adaptive': False,
        'alpha0': 1.0,
        'alpha1': 0.1,
        'prob1': 0.01,
        'help': False
    }

    def error(self, message):
        sys.stderr.write(message[0].capitalize() + message[1:] + '\n')
        sys.stderr.write('Use "arhc.py --help" to view more information.\n')
        exit()

    def parseArguments(self):
        iterator = iter(sys.argv[1:]) # Skip file name
        for argument in iterator:
            if len(argument) < 2 or argument[:2] != '--':
                self.error('syntax error "{}"'.format(argument))
            else:
                getValueOfArgument = lambda: next(iterator)
                self.parseArgument(argument[2:], getValueOfArgument)

    def parseArgument(self, argument, getValueOfArgument):
        if argument in self.arguments:
            if type(self.arguments[argument]) == bool:
                self.arguments[argument] = True
            else:
                self.arguments[argument] = self.castType(type(self.arguments[argument]), getValueOfArgument())
        else:
            self.error('unknown argument "--{}"'. format(argument))

    def castType(self, valueType, value):
        try:
            return valueType(value)
        except ValueError:
            self.error('incorrect type "{}"'.format(value))

    def run(self):
        if self.arguments['help']:
            sys.stdout.write(self.usage)
        else:
            if self.arguments['adaptive']:
                arhc = ARHC(AdaptiveProbability(self.arguments['alpha0'], self.arguments['alpha1']))
            else:
                arhc = ARHC(ConstantProbability(self.arguments['prob1']))
            streams = (Stream(sys.stdin, self.arguments['N']), Stream(sys.stdout, self.arguments['N']))
            if self.arguments['decompress']:
                arhc.decompress(*streams)
            else:
                arhc.compress(*streams)


if __name__ == '__main__':
    main = Main()
    main.parseArguments()
    main.run()
    time.sleep(0.01) # Keep process alive for just another bit

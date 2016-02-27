#!/usr/bin/env python

import sys
import math


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


class Huffman:
    def __init__(self, words):
        self.words = words
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

    def getPredictive1(self):
        return self.prob1

    def getRunLength(self):
        return self.runLength

    def observe(self, string):
        pass


class ARHC:
    N = 10000
    # p = AdaptiveProbability(0.1, 0.1)
    p = ConstantProbability(0.01, 69)

    def __init__(self, inStream, outStream):
        self.inStream = Stream(inStream, self.N)
        self.outStream = Stream(outStream, self.N)
        self.buildHuffman()

    def buildHuffman(self):
        prob1 = self.p.getPredictive1()
        runLength = self.p.getRunLength()
        self.words = [Word('0' * runLength, pow(1 - prob1, runLength))]
        for i in range(runLength + 1):
            self.words.append(Word('0' * i + '1', pow(1 - prob1, i) * prob1))
        self.words.append(Word('EOT', 1.0 / (prob1 * self.N + 1)))
        self.huff = Huffman(self.words)

    def compress(self):
        self.inStream.attachRead(self.p.observe)
        while self.inStream.areBitsLeftToRead():
            self.outStream.write(self.huff.encode(self.inStream))
            self.buildHuffman()

    def decompress(self):
        self.outStream.attachWrite(self.p.observe)
        word = self.huff.decode(self.inStream)
        while word != 'EOT':
            self.outStream.write(word)
            self.buildHuffman()
            word = self.huff.decode(self.inStream)
        while self.outStream.areBitsLeftToWrite():
            self.outStream.write('0')


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

    def areBitsLeftToRead(self):
        return self.bitsRead < self.N

    def areBitsLeftToWrite(self):
        return self.bitsWritten < self.N

    def attachRead(self, observer):
        self.observerRead = observer

    def attachWrite(self, observer):
        self.observerWrite = observer

    

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '--compress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.compress()
    elif sys.argv[1] == '--decompress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.decompress()
    else:
        sys.stderr.write('Undefined behaviour\n')


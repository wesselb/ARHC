#!/usr/bin/env python

import sys


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


class ARHC:
    N = 10000
    n = 69
    p = 0.01

    def __init__(self, inStream, outStream):
        self.inStream = Stream(inStream, self.N)
        self.outStream = Stream(outStream, self.N)
        self.buildHuffman()


    def buildHuffman(self):
        self.words = [Word('0' * self.n, pow(1 - self.p, self.n))]
        for i in range(self.n + 1):
            self.words.append(Word('0' * i + '1', pow(1 - self.p, i) * self.p))
        self.words.append(Word('EOT', 1.0/(self.p*self.N)))
        self.huff = Huffman(self.words)

    def compress(self):
        while self.inStream.areBitsLeftToRead():
            self.outStream.write(self.huff.encode(self.inStream))

    def decompress(self):
        word = self.huff.decode(self.inStream)
        while word != 'EOT':
            self.outStream.write(word)
            word = self.huff.decode(self.inStream)
        while self.outStream.areBitsLeftToWrite():
            self.outStream.write('0')


class Stream:
    bitsRead = 0
    bitsWritten = 0

    def __init__(self, stream, N):
        self.stream = stream
        self.N = N

    def read(self, num=1):
        self.bitsRead += num
        return self.stream.read(num)

    def write(self, string):
        self.bitsWritten += len(string)
        self.stream.write(string)

    def areBitsLeftToRead(self):
        return self.bitsRead < self.N

    def areBitsLeftToWrite(self):
        return self.bitsWritten < self.N

    

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '--compress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.compress()
    elif sys.argv[1] == '--decompress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.decompress()
    else:
        sys.stderr.write('Undefined behaviour\n')


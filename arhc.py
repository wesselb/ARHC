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
    
    def getEncoding(self, suffix=''):
        return self.left.getEncoding('0' + suffix) + self.right.getEncoding('1' + suffix)

    def decode(self, stream):
        if stream.read(1) == '0':
            return self.left.decode(stream)
        else:
            return self.right.decode(stream)


class Huffman:
    def __init__(self, words):
        self.words = words
        self.build()

    def build(self):
        while len(self.words) > 1:
            # Merge two lowest probability words
            self.words.sort(key=lambda word: word.getProb())
            self.words.insert(0, MergedWord(self.words.pop(), self.words.pop()))
        self.encoding = dict(self.words[0].getEncoding())

    def encode(self, string):
        return self.encode[string]

    def decode(self, stream):
        return self.words[0].decode(stream)


class ARHC:
    N = 10000
    
    def __init__(self, inStream, outStream):
        self.inStream = inStream
        self.outStream = outStream

    def compress(self):
        huff = Huffman([Word('0', 0.3), Word('10', 0.2), Word('11', 0.5)])
        self.outStream.write(self.inStream.read(self.N))

    def decompress(self):
        self.outStream.write(self.inStream.read(self.N))
    

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '--compress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.compress()
    elif sys.argv[1] == '--decompress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.decompress()
    else:
        sys.stderr.write('Undefined behaviour\n')


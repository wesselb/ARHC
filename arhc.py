#!/usr/bin/env python

import sys


class Word:
    def __init__(self, word, prob):
        self.word = word
        self.prob = prob

    def getProb(self):
        return self.prob

class EquivalentWord:
    def __init__(self, word1, word2):
        self.word1 = word1
        self.word2 = word2

    def getProb(self):
        return self.word1.getProb() + self.word2.getProb()



class Huffman:
    def __init__(self, words):
        self.words = words




class ARHC:
    N = 10000
    
    def __init__(self, inStream, outStream):
        self.inStream = inStream
        self.outStream = outStream

    def compress(self):
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


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
        nextBit = stream.read(1)
        if nextBit == '0':
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
            self.words.insert(0, MergedWord(self.words.pop(0), self.words.pop(0)))
        self.encoding = dict(self.words[0].getEncoding())

    def encode(self, string):
        return self.encoding[string]

    def decode(self, stream):
        return self.words[0].decode(stream)


class ARHC:
    N = 500#10000
    n = 69
    p = 0.01
    
    def __init__(self, inStream, outStream):
        self.inStream = inStream
        self.outStream = outStream
        self.buildWords()
        self.huff = Huffman(self.words)

    def buildWords(self):
        self.words = [Word('0' * self.n, pow(1 - self.p, self.n))]
        for i in range(self.n):
            self.words.append(Word('0' * i + '1', pow(1 - self.p, i) * self.p))
        self.words.append(Word('EOT', 1.0/self.N))
        self.buildTree()

    def buildTree(self):
        self.root = MergedWord(self.words[0], self.words[self.n - 1])
        for i in range(2, self.n):
            self.root = MergedWord(self.root, self.words[self.n - i])

    def compress(self):
        inBits = self.inStream.read(self.N)
        if inBits[-1] == '0':
            self.outStream.write('1')
            inBits = inBits[:-1] + '1'
        else:
            self.outStream.write('0')
        stream = Stream(inBits) 
        while stream.bitsRead < self.N:
            self.outStream.write(self.huff.encode(self.root.decode(stream)))
        self.outStream.write(self.huff.encode('EOT'))

    def decompress(self):
        fb = self.inStream.read(1)
        prev = ''
        while True:
            cur = self.huff.decode(self.inStream)
            if cur == 'EOT':
                if fb == '1':
                    self.outStream.write(prev[:-1] + '0')
                else:
                    self.outStream.write(prev)
                break
            self.outStream.write(prev)
            prev = cur


class Stream:
    bitsRead = 0
    def __init__(self, string):
        self.string = string

    def read(self, num=1):
        self.bitsRead += num
        ret = self.string[0:num]
        self.string = self.string[num:]
        return ret

    def getBitsRead(self):
        return self.bitsRead
    

if __name__ == '__main__':
    if len(sys.argv) == 1 or sys.argv[1] == '--compress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.compress()
    elif sys.argv[1] == '--decompress':
        arhc = ARHC(sys.stdin, sys.stdout)
        arhc.decompress()
    else:
        sys.stderr.write('Undefined behaviour\n')


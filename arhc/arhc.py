import math
from leaf import Leaf
from huffman import Huffman


class ARHC:

    """
    Implementation of Adaptive Run-length Huffman Compressor.

    :param prob1: Probability of one.
    """

    def __init__(self, prob1):
        self.prob1 = prob1

    def calculateOptimalRunLength(self):
        """ Calculate the optimal run-length. """
        return int(round(math.log(0.5) /
                         math.log(1 - self.prob1.getPredictive1())))

    def buildSymbols(self, runLength):
        """ Build an alphabet encoding run-lengths. """
        symbols = [Leaf(
            '0' * runLength,
            pow(1 - self.prob1.getPredictive1(), runLength)
        )]
        for i in range(runLength + 1):
            symbols.append(Leaf(
                '0' * i + '1',
                pow(1 - self.prob1.getPredictive1(), i) *
                self.prob1.getPredictive1()
            ))
        return symbols

    def buildHuffman(self, bitsLeft):
        """ Build a Huffman symbol code from an alphabet that encodes
            run-lengths. """
        runLength = min(bitsLeft, self.calculateOptimalRunLength())
        symbols = self.buildSymbols(runLength)
        self.huffman = Huffman(symbols)

    def compress(self, inStream, outStream):
        """ Compress the contents of a stream and write the compressed
            contents to another stream. """
        inStream.observeRead(self.prob1.observe)
        while inStream.bitsLeftToRead() > 0:
            self.buildHuffman(inStream.bitsLeftToRead())
            outStream.write(self.huffman.encode(inStream))

    def decompress(self, inStream, outStream):
        """ Decompress the contents of a stream and write the decompressed
            contents to another stream. """
        outStream.observeWrite(self.prob1.observe)
        while outStream.bitsLeftToWrite() > 0:
            self.buildHuffman(outStream.bitsLeftToWrite())
            outStream.write(self.huffman.decode(inStream))

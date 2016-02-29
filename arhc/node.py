class Node:

    """
    Encapsulation of a combined pair of symbols as in the Huffman algorithm.
    When used in conjunction with Leaf it acts as non-leaf node of a binary
    tree.

    :param left:  First symbol in the pair of combined symbols that will be
                  appended '0' in its encoding.
    :param right: Second symbol in the pair of combined symbols that will be
                  appended '1' in its encoding.
    """

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def getProb(self):
        """ Get probability of the combined pair of symbols. """
        return self.left.getProb() + self.right.getProb()

    def getEncoding(self, prefix=''):
        """ Get encoding of all symbols contained in the subtree below this
            node, as defined by the subtree below this node. """
        return self.left.getEncoding(prefix + '0') + \
            self.right.getEncoding(prefix + '1')

    def decode(self, stream):
        """ Get the first symbol from the stream that is encoded by the
            subtree below this node. """
        if stream.read() == '0':
            return self.left.decode(stream)
        else:
            return self.right.decode(stream)

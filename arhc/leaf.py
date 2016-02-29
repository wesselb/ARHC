class Leaf:

    """
    Encapsulation of a symbol in a symbol code. When used in conjunction with
    Node it acts as the leaf of a binary tree.

    :param symbol: String representation of the symbol.
    :param prob:   Probability of the symbol.
    """

    def __init__(self, symbol, prob):
        self.prob = prob
        self.symbol = symbol

    def getProb(self):
        """ Get probability of the symbol. Acts as the base case in finding
            the probability of a tree. """
        return self.prob

    def getEncoding(self, encoding):
        """ Get encoding of the symbol. Acts as the base case in finding the
            encoding of all symbols of a tree as defined by that tree. """
        return [(self.symbol, encoding)]

    def decode(self, stream):
        """ Return the string that represents the symbol. Acts as the base
            case in decoding the tree. """
        return self.symbol

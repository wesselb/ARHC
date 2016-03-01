class ConstantProbability:

    """
    Fixed probability of one.

    :param prob1: Probability of one.
    """

    def __init__(self, prob1):
        self.prob1 = prob1

    def observe(self, string):
        """ Do nothing since the probability of one is fixed. """
        pass

    def getPredictive1(self):
        """ Get predictive probability of one. """
        return self.prob1


class AdaptiveProbability:

    """
    Keeps track of the belief about the probability of one. Uses
    p ~ Beta(alpha0, alpha1) as the prior distribution. Updates via Ber(p)
    likelihood.

    :param alpha0: Pseudo-count associated with the probability of zero.
    :param alpha1: Pseudo-count associated with the probability of one.
    """

    def __init__(self, alpha0, alpha1):
        self.alpha0 = float(alpha0)
        self.alpha1 = float(alpha1)

    def observe(self, string):
        """ Update belief according to an observation. """
        observed1 = sum(map(int, string))
        self.alpha0 += len(string) - observed1
        self.alpha1 += observed1

    def getPredictive1(self):
        """ Find the predictive probability of one. """
        return self.alpha1 / (self.alpha0 + self.alpha1)

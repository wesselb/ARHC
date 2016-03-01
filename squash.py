#!/usr/bin/env python

import sys
import textwrap
import time
from arhc.arhc import ARHC
from arhc.probability import ConstantProbability, AdaptiveProbability
from arhc.stream import Stream


class Main:

    """
    Parsing of command-line arguments and invoking the ARHC.
    """

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
        --alpha0 value       Pseudo-count associated with the probability of
                             zero, default 0.5
        --alpha1 value       Pseudo-count associated with the probability of
                             one, default 0.5

    Details:
        Compresses by default. Uses static compression scheme by default.
    ''')

    arguments = {
        'decompress': False,
        'N':          10000,
        'adaptive':   False,
        'alpha0':     0.5,
        'alpha1':     0.5,
        'prob1':      0.01,
        'help':       False
    }

    def error(self, message):
        """ Display an error message and terminate. """
        sys.stderr.write(message[0].capitalize() + message[1:] + '\n')
        sys.stderr.write('Use "arhc.py --help" to view more information.\n')
        exit()

    def parseArguments(self):
        """ Loop through the arguments and verify their syntax. """
        iterator = iter(sys.argv[1:])  # Skip file name
        for argument in iterator:
            if len(argument) < 2 or argument[:2] != '--':
                self.error('syntax error "{}"'.format(argument))
            else:
                def getValueOfArgument(): return next(iterator)
                self.parseArgument(argument[2:], getValueOfArgument)

    def parseArgument(self, argument, getValueOfArgument):
        """ Parse an argument and its value. """
        if argument in self.arguments:
            if type(self.arguments[argument]) == bool:
                self.arguments[argument] = True
            else:
                self.arguments[argument] = self.castType(
                    type(self.arguments[argument]), getValueOfArgument())
        else:
            self.error('unknown argument "--{}"'. format(argument))

    def castType(self, valueType, value):
        """ Cast a value to a type. """
        try:
            return valueType(value)
        except (ValueError, TypeError):
            self.error('incorrect type "{}"'.format(value))

    def run(self):
        """ Top-level logic of the ARHC. """
        self.parseArguments()
        if self.arguments['help']:
            sys.stdout.write(self.usage)
        else:
            if self.arguments['adaptive']:
                arhc = ARHC(AdaptiveProbability(
                    self.arguments['alpha0'], self.arguments['alpha1']))
            else:
                arhc = ARHC(ConstantProbability(self.arguments['prob1']))
            streams = (Stream(sys.stdin, self.arguments['N']), Stream(
                sys.stdout, self.arguments['N']))
            if self.arguments['decompress']:
                arhc.decompress(*streams)
            else:
                arhc.compress(*streams)


if __name__ == '__main__':
    main = Main()
    main.run()
    time.sleep(0.1)  # Keep process alive for just another bit

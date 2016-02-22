#!/usr/bin/env python

import subprocess
import sys


def main():
    with open('input.txt', 'r') as f:
        bitsIn = f.read().strip()
    with open('compressed.txt', 'r') as f:
        bitsCompressed = f.read().strip()
    with open('decompressed.txt', 'r') as f:
        bitsDecompressed = f.read().strip()    


    print('Input bits:        {:d}'.format(len(bitsIn)))
    print('Compressed bits:   {:d}'.format(len(bitsCompressed)))

    ratio = 1 - float(len(bitsCompressed))/len(bitsIn)
    print('Compression ratio: {:.3f}'.format(ratio))

    print('Match:             {:s}'.format(
        'yes' if bitsIn == bitsDecompressed else 'no'))


if __name__ == '__main__':
    main()

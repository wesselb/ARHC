#!/usr/bin/env bash

./arhc.py --compress < input2.txt > compressed.txt
./arhc.py --decompress < compressed.txt > decompressed.txt

./evaluate.py

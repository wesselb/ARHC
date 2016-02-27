#!/usr/bin/env bash

./arhc.py --compress < input.txt > compressed.txt
./arhc.py --decompress < compressed.txt > decompressed.txt

./evaluate.py

#!/usr/bin/env bash

echo Adaptive
echo ----------------
./arhc.py --adaptive < input.txt > compressed.txt
./arhc.py --decompress --adaptive < compressed.txt > decompressed.txt
./evaluate.py


echo
echo Static
echo ----------------
./arhc.py < input.txt > compressed.txt
./arhc.py --decompress < compressed.txt > decompressed.txt
./evaluate.py

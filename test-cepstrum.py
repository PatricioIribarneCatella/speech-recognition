#!/usr/bin/env python3

from signal import Signal

def main():

    s = Signal(path="./waves/fantasia.wav")
    s.cepstrogram()

if __name__ == "__main__":
    main()


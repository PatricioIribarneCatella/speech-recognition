#!/usr/bin/env python3

from signal import Signal

def main():

    s = Signal(path="./waves/fantasia.wav")
    s.spectrogram()
    s.cepstrogram()
    s.lpctrogram()

if __name__ == "__main__":
    main()


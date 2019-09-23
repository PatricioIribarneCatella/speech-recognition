#!/usr/bin/env python3

from signal import Signal

def main():

    s = Signal()
    s.synthesize()
    s.cepstrum()
    #s.export("synt.wav")

if __name__ == "__main__":
    main()


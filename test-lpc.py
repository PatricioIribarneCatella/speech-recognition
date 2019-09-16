#!/usr/bin/env python3

from signal import Signal

def main():

    s = Signal(path="./waves/fantasia.wav")
    s.plot(name="original")
    r = s.lpc_encode()

    new = Signal()
    new.lpc_decode(r)
    new.export("new.wav")
    new.plot(name="new")

if __name__ == "__main__":
    main()


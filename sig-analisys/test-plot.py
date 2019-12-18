#!/usr/bin/env python3

from signal import Signal

def main():

    s = Signal(path="../HTK/gf-records/1.wav")

    s.plot("time", name="time-rec", title="Llame a Andres", xlabel="t [s]", ylabel="Amp", pictfmt="png")

if __name__ == "__main__":
    main()


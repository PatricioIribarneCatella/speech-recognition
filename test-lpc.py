#!/usr/bin/env python3

from signal import Signal

def main():

    title="Time plot"
    xlabel="Time [s]"
    ylabel="Amplitud"

    s = Signal(path="./waves/fantasia.wav")
    s.plot("time", name="original", title=title, xlabel=xlabel, ylabel=ylabel)
    r = s.encode()

    new = Signal()
    new.decode(r)
    new.export("new.wav")
    new.plot("time", name="new", title=title, xlabel=xlabel, ylabel=ylabel)

if __name__ == "__main__":
    main()


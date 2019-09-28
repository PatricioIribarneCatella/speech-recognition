#!/usr/bin/env python3

from signal import Signal

def main():

    s = Signal(path="./waves/fantasia.wav")
    s.plot("spectrogram", name="spect", title="Spectrogram")
    s.plot("cepstrogram", name="cepst", title="Cepstrogram")
    s.plot("lpctrogram", name="lpct", title="LPCtrogram")

if __name__ == "__main__":
    main()


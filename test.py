from signal import Signal

def main():

    s = Signal(path="./waves/s0.wav")

    s.plot()
    s.frequency()
    s.spectrogram()

if __name__ == "__main__":
    main()


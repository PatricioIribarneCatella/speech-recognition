import numpy as np
from scipy.io.wavfile import read as wavread, write as wavwrite

def load(path):

    Fs, x = wavread(path)

    if x.dtype == 'int16':
        nb_bits = np.float(16)
        x = x / 2**(nb_bits-1)
    elif x.dtype == 'int32':
        nb_bits = np.float(32)
        x = x / 2**(nb_bits-1)
    elif x.dtype == 'uint8':
        x = x / 2**8

    x = x.astype(np.float64)

    return x, Fs

def export(x, Fs, name):

    wavwrite(name, Fs, x)

# computes the FFT
def fft(x, nfft=None):
    return np.fft.fft(x, len(x) if nfft is None else nfft)

# computes the IFFT
def ifft(x):
    return np.fft.ifft(x)

def sampler(x, Fs, resolve, **kwargs):

    samples_window = round(Fs * 0.025)
    t = np.arange(len(x)) / Fs
    end_time = t[-1]
    samples = []

    for offset in np.arange(0.0, end_time - 0.025, 0.010) * Fs:

        offset = int(offset)

        # Gets signal window at [offset:offset+samples_window)
        window = x[offset:(offset + samples_window)]

        res = resolve(window, kwargs)

        samples.append(res)

    H_mat = np.array(samples).T

    return H_mat


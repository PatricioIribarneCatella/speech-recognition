import numpy as np

from matplotlib import pyplot as plt

from scipy.io.wavfile import read as wavread, write as wavwrite
from scipy.signal import spectrogram

class Signal(object):

    def __init__(self, x=np.array([]), Fs=1.0, t0=0.0, path=None):
        
        if path is not None:
            
            # signal should be imported
            # from a WAV file

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
        else:
            # signal should be taken
            # from the 'x' argument

            x = x.astype(np.float64)

        self.x = x
        self.Fs = Fs
        self.L = np.size(self.x)
        self.t = np.arange(self.L) / self.Fs + t0

    def plot(self, title='Time plot', name='time-plot'):

        fig, ax = plt.subplots()
        
        fig.suptitle(title)
        ax.plot(self.t, self.x)
        ax.set(xlabel='Time [s]', ylabel='Amplitud')

        plt.savefig("{}.png".format(name))

    def frequency(self, title='Frequecy plot', name='freq-plot'):

        # Hertz
        X = self.fft() / self.L
        X = X[range(self.L // 2)]

        k = np.arange(self.L // 2)
        frq = k * self.Fs / self.L

        fig, ax = plt.subplots()

        fig.suptitle(title)
        ax.plot(frq, np.abs(X))
        ax.set(xlabel='Frequecy [Hz]', ylabel='Energy')

        plt.savefig("{}.png".format(name))

    def spectrogram(self, title='Spectrogram plot', name='spectr-plot',
                    ax=None, window='hanning', t_window=0.025, t_overlap=0.0,
                    Nfft=None, detrend='constant', return_onesided=True,
                    scaling='density', axis=-1, mode='psd'):

        n_perseg = int(t_window * self.Fs)
        n_overlap = int(t_overlap * self.Fs)

        if Nfft is None:
            Nfft = n_perseg * 8

        f, t, Sxx = spectrogram(self.x, window=window, fs=self.Fs,
                                nperseg=n_perseg, noverlap=n_overlap, nfft=Nfft,
                                detrend=detrend, return_onesided=return_onesided,
                                scaling=scaling, axis=axis, mode=mode)

        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)

        fig.suptitle(title)
        ax.pcolormesh(t, f, np.log(np.abs(Sxx)))
        ax.set(xlabel='Time [s]', ylabel='Frequecy [Hz]')
        ax.plot()

        plt.savefig("{}.png".format(name))

    def fft(self, Nfft=0):

        return np.fft.fft(self.x, self.L if Nfft <= 0 else Nfft)

    def export(self, name):

        wavwrite(name, self.Fs, self.x)


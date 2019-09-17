import numpy as np

from matplotlib import pyplot as plt

from scipy.io.wavfile import read as wavread, write as wavwrite
from scipy.signal import spectrogram, freqz, lfilter
from scipy.linalg import toeplitz, inv

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

    def _fft(self, x, Nfft=0):
        
        L = len(x)

        return np.fft.fft(x, L if Nfft <= 0 else Nfft) / L

    def _plot(self, X, Y, title=None, name=None, xlabel=None, ylabel=None):

        fig, ax = plt.subplots()
        
        fig.suptitle(title)
        ax.plot(X, Y)
        ax.set(xlabel=xlabel, ylabel=ylabel)

        plt.savefig("{}.png".format(name))
    
    def _plot_samples_debug(self, plot_samples, window, a, gain, offset):

        if plot_samples:
            
            # Frequecy from the Filter
            w, h = freqz([gain], [1] + list(a*(-1)))

            # Frequecy from the FFT of the window
            window_fft = self._fft(window, len(window))
            window_fft = window_fft[range(len(window) // 2)]

            k = np.arange(len(window) // 2)
            frq = k * self.Fs / len(window)

            # Plot frequency
            fig, (ax, ay) = plt.subplots(2)

            plt.subplots_adjust(hspace=0.4)

            fig.suptitle("Frequecy Domain plot - offset: {}".format(offset))

            ax.set_title("Frequecy for LPC coefficients filter")
            ax.plot(w*self.Fs/(2*np.pi), np.abs(h))
            ax.set(ylabel='Energy')

            ay.set_title("Frequecy for window FFT")
            ay.plot(frq, np.abs(window_fft))
            ay.set(xlabel='Frequecy [Hz]', ylabel='Energy')

            plt.savefig("./plots/freq-lpc-offset-{}.png".format(offset))
            plt.close(fig)
    
    def _quantify(self, x, N):

        x_norm = (x - np.min(x)) / (np.max(x) - np.min(x))

        return np.floor(x_norm * (2**N)) * (np.max(x) - np.min(x)) / (2**N) + np.min(x)

    def get_samples(self):

        return self.x

    def plot(self, title='Time plot', name='time-plot'):

        self._plot(self.t, self.x, title, name, xlabel="Time [s]", ylabel="Amplitud")

    def frequency(self, title='Frequecy plot', name='freq-plot'):

        X = self._fft(self.x)
        X = X[range(self.L // 2)]

        k = np.arange(self.L // 2)
        frq = k * self.Fs / self.L

        self._plot(frq, np.abs(X), title, name, xlabel='Frequecy [Hz]', ylabel='Energy')

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

        return self._fft(self.x, Nfft)

    def encode(self, M=20, N=8, plot_samples=False):

        """
            It uses LPC (Linear Predictive Coding)
        """

        samples_window = round(self.Fs * 0.025)
       
        end_time = self.t[-1]

        res = []
        zi = np.zeros(19)

        for offset in np.arange(0.0, end_time - 0.025, 0.010) * self.Fs:
           
            offset = int(offset)

            # Gets signal window at [offset:offset+samples_window)
            window = self.x[offset:(offset + samples_window)]
            
            # Finds the correlation function
            # which will be used for 'rho' stimation
            rho = np.correlate(window, window, "full")
            
            # The 'M' rho stimators are taken from
            # the middle of the correlation function
            stimate = rho[len(rho)//2:(len(rho)//2 + M)]

            # Build the 'toeplitz' matrix.
            # Find its inverse and calculate
            # the 'a' coefficients
            mat = toeplitz(stimate[:(M-1)])
            a = inv(mat).dot(stimate[1:])

            # Calculates the 'gain' filter parameter
            gain = stimate[0]

            for i in range(1, len(a)):
                gain += stimate[i] * a[i]

            ten_samples = round(self.Fs * 0.010)
            ten_window = window[:ten_samples]
    
            # filterd 10ms window
            ten_filt, zi = lfilter([0] + list(a), [1], ten_window, zi=zi)
            err = ten_window - ten_filt

            x = self._quantify(err / gain, N)

            # Save sample results
            s = {
                "x": list(x),
                "a": list(a),
                "G": gain
            }
            
            res.append(s)

            self._plot_samples_debug(plot_samples, window, a, gain, offset)

        return res

    def decode(self, samples):

        signal = np.array([])
    
        zi = np.zeros(19)

        for s in samples:

            gain = s["G"]
            a = np.array(s["a"])
            x = s["x"]

            win, zi = lfilter([1], [1] + list(a*(-1)), np.array(x) * gain, zi=zi)

            signal = np.concatenate((signal, win))

        self.x = np.array(signal)
        self.Fs = 16000
        self.L = np.size(self.x)
        self.t = np.arange(self.L) / self.Fs

    def convolve(self, s, mode="full"):
        
        x = s.get_samples()

        conv = np.convolve(self.x, x, mode)

        return Signal(conv, self.Fs)

    def export(self, name):

        wavwrite(name, self.Fs, self.x)


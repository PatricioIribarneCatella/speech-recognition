import numpy as np

from matplotlib import pyplot as plt

from scipy.io.wavfile import read as wavread, write as wavwrite
from scipy.signal import spectrogram, freqz
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

    def lpc(self, M=20, plot_samples=False):

        samples_window = round(self.Fs * 0.025)
       
        end_time = self.t[-1]

        res = []

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

            # Frequecy from the Filter
            w, h = freqz([gain], [1] + list(a*(-1)))

            # Frequecy from the FFT of the window
            window_fft = np.fft.fft(window, len(window)) / len(window)
            window_fft = window_fft[range(len(window) // 2)]

            # Save sample results
            s = {
                "M": M,
                "a": list(a),
                "G": gain,
                "H": np.abs(h),
                "H-fft": np.abs(window_fft)
            }
            res.append(s)

            if plot_samples:

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

        return res

    def zeropole(self):
        return 0

    def convolve(self):
        return 0

    def export(self, name):

        wavwrite(name, self.Fs, self.x)


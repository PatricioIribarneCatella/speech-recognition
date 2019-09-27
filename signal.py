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

        return np.fft.fft(x, L if Nfft <= 0 else Nfft)

    def _ifft(self, X):

        return np.fft.ifft(X)

    def _plot(self, X, Y, title=None, name=None, xlabel=None, ylabel=None):

        fig, ax = plt.subplots()
        
        fig.suptitle(title)
        ax.plot(X, Y)
        ax.set(xlabel=xlabel, ylabel=ylabel)

        plt.savefig("{}.svg".format(name))
    
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
        zi = np.zeros(M - 1)

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

    def decode(self, samples, M=20):

        signal = np.array([])
    
        zi = np.zeros(M - 1)

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

    def synthesize(self):

        self.Fs = 16000
        Ts = 1/self.Fs
        
        # Entrada: tren de impulsos
        F0 = 130
        t = np.arange(self.Fs) * Ts
        p = np.zeros(len(t))
        for i in range(len(p)):
            p[i] = 1 if i % F0 == 0 else 0
        
        self._plot(t, p, xlabel="t", name="p", title="p(n)")

        # Modelo del tracto vocal
        Fk_sigmak = np.array([(660, 60),(1720, 100),(2410, 120),(3500, 175),(4500, 250)])
        
        filters = []
        for Fk, sigmak in Fk_sigmak:
            rho = np.exp(-2 * np.pi * sigmak * Ts)
            filters.append(np.array([1, -2* rho * np.cos(2 * np.pi * Fk * Ts), rho**2]))

        V = np.array(filters[0])
        for f in range(1, len(filters)):
            conv = np.convolve(V, filters[f])
            V = conv

        # Frequecy from the V filter
        w, h = freqz([1], V)
        self._plot(w*self.Fs/(2*np.pi), np.abs(h), xlabel="f", name="V", title="V(z)")

        # Radiación labial
        R = np.array([1, -0.96])

        # Frequecy from the R filter
        w, h = freqz(R, [1])
        self._plot(w*self.Fs/(2*np.pi), np.abs(h), xlabel="f", name="R", title="R(z)")
       
        # Frequecy from the R/V filter
        w, h = freqz(R, V)
        self._plot(w*self.Fs/(2*np.pi), np.abs(h), xlabel="f", name="R.V", title="R(z)/V(z)")
        
        # Respuesta del modelo completo
        # s = p * v * r == S(z) = P(z).V(z).R(z)
 
        self.x = lfilter(R, V, p)
        
        self.L = np.size(self.x)
        self.t = np.arange(self.L) / self.Fs
       
        # s(n) in time
        self._plot(self.t, self.x, xlabel="t", ylabel="amplitud", name="s", title="s(n)")

    def cepstrum(self, N=80):
        
        S = self._fft(self.x, Nfft=8*len(self.x))

        freq = np.arange(len(S)) * self.Fs / len(S)
        
        # S(z) frequency
        self._plot(freq, np.abs(S), xlabel="f", ylabel="Energy", name="S", title="S(z)")

        _s = self._ifft(np.log(np.abs(S)))

        t = np.arange(len(_s)) / self.Fs

        self._plot(t, np.abs(_s), xlabel="t", ylabel="amplitud", name="_s", title="_s(n)")

        # Build time filter
        # to remove the x part
        filt = np.zeros(len(_s))

        for i in range(N):
            filt[i] = 1
        for i in range(len(filt)-(N-1), len(filt)):
            filt[i] = 1

        _h = _s * filt

        self._plot(t, np.abs(_h), xlabel="t", ylabel="amplitud", name="_h", title="_h(n)")

        _H = np.exp(np.abs(self._fft(_h)))
        
        # _H(z) frequency
        freq = np.arange(len(_H)) * self.Fs / len(_H)
 
        self._plot(freq, np.abs(_H), xlabel="f", ylabel="Energy", name="_H", title="_H(z)")

        fig, ax = plt.subplots()
        
        fig.suptitle("_H(z), S(z)")
        ax.plot(freq, np.abs(S) / np.max(np.abs(S)), 'r', freq, np.abs(_H) / np.max(np.abs(_H)), 'b')
        ax.set(xlabel="f", ylabel="Energy")

        plt.savefig("{}.svg".format("_HandS"))

    def _plot_cepstrogram(self, H_samples):

        NF, NT = H_samples.shape

        f = np.arange(NF) * self.Fs / NF
        t = np.arange(NT) * 0.010

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

        fig.suptitle("Cepstrogram")
        ax.pcolormesh(t, f, np.log(np.abs(H_samples)))
        ax.plot()
        ax.set(xlabel='Time [s]', ylabel='Frequecy [Hz]')
        ax.set_ylim(0, self.Fs//2)

        plt.savefig("{}.png".format("cepstrogram"))

    def cepstrogram(self, N=80):

        samples_window = round(self.Fs * 0.025)
       
        end_time = self.t[-1]

        res = []

        for offset in np.arange(0.0, end_time - 0.025, 0.010) * self.Fs:

            offset = int(offset)

            # Gets signal window at [offset:offset+samples_window)
            window = self.x[offset:(offset + samples_window)]

            # Gets the FFT of the window
            S_win = self._fft(window, Nfft=8*len(window))

            # Gets the cepstrum _s(n) = IFFT(log(|S|))
            _s = self._ifft(np.log(np.abs(S_win)))

            # Build time filter
            # to remove the x part
            filt = np.zeros(len(_s))

            for i in range(N):
                filt[i] = 1
            for i in range(len(filt)-(N-1), len(filt)):
                filt[i] = 1

            _h = _s * filt

            # Gets the FFT of the _h
            _H = np.abs(np.exp(self._fft(_h)))

            res.append(_H)

        H_mat = np.array(res).T
        self._plot_cepstrogram(H_mat)

    def _plot_lpctrogram(self, H_samples):

        NF, NT = H_samples.shape

        f = np.arange(NF) * (self.Fs / 2) / NF
        t = np.arange(NT) * 0.010

        fig = plt.figure()
        ax = fig.add_subplot(1,1,1)

        fig.suptitle("LPC-trogram")
        ax.pcolormesh(t, f, np.log(np.abs(H_samples)))
        ax.plot()
        ax.set(xlabel='Time [s]', ylabel='Frequecy [Hz]')
        ax.set_ylim(0, self.Fs/2)

        plt.savefig("{}.png".format("lpctrogram"))

    def lpctrogram(self):

        r = self.encode()
        res = []

        for sample in r:

            gain = sample["G"]
            a = np.array(sample["a"])

            # Frequecy from the Filter
            w, h = freqz([1], [1] + list(a*(-1)))

            res.append(np.abs(h)*gain)
        
        H_mat = np.array(res).T
        self._plot_lpctrogram(H_mat)

    def convolve(self, s, mode="full"):
        
        x = s.get_samples()

        conv = np.convolve(self.x, x, mode)

        return Signal(conv, self.Fs)

    def export(self, name):

        wavwrite(name, self.Fs, self.x)


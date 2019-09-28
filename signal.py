import numpy as np

from scipy.signal import spectrogram, freqz, lfilter
from scipy.linalg import toeplitz, inv

from plotting import plot, plot_xtrogram
from utils import fft, ifft, sampler, load, export

class Signal(object):

    def __init__(self, x=np.array([]), Fs=1.0, t0=0.0, path=None):
        
        if path is not None:
            # signal should be imported
            # from a WAV file
            x, Fs = load(path)
        else:
            # signal should be taken
            # from the 'x' argument
            x = x.astype(np.float64)

        self.x = x
        self.Fs = Fs
        self.L = np.size(self.x)
        self.t = np.arange(self.L) / self.Fs + t0

        self.PLOTS = {
                "time": self._plot_time,
                "frequency": self._plot_freq,
                "spectrogram": self._plot_spec,
                "cepstrogram": self._plot_cepstrogram,
                "lpctrogram": self._plot_lpctrogram
        }

    def _quantify(self, x, N):

        x_norm = (x - np.min(x)) / (np.max(x) - np.min(x))

        return np.floor(x_norm * (2**N)) * (np.max(x) - np.min(x)) / (2**N) + np.min(x)

    def _plot_time(self, kwargs):

        plot(self.t, self.x, kwargs)

    def _plot_freq(self, kwargs):

        X = fft(self.x)
        X = X[range(self.L // 2)]

        k = np.arange(self.L // 2)
        frq = k * self.Fs / self.L

        plot(frq, np.abs(X), kwargs)

    def _plot_spec(self, kwargs):

        n_perseg = int(0.025 * self.Fs)
        window = 'hanning'
        detrend = 'constant'
        return_onesided = True
        scaling = 'density'
        axis = -1
        mode = 'psd'
        Nfft = n_perseg * 8

        f, t, Sxx = spectrogram(self.x, window=window, fs=self.Fs,
                                nperseg=n_perseg, nfft=Nfft,
                                detrend=detrend, return_onesided=return_onesided,
                                scaling=scaling, axis=axis, mode=mode)

        plot_xtrogram(t, f, Sxx, self.Fs, kwargs)

    def _plot_cepstrogram(self, kwargs):

        H_mat = self.cepstrogram()

        NF, NT = H_mat.shape

        f = np.arange(NF) * self.Fs / NF
        t = np.arange(NT) * 0.010

        plot_xtrogram(t, f, H_mat, self.Fs, kwargs)

    def _plot_lpctrogram(self, kwargs):

        H_mat = self.lpctrogram()

        NF, NT = H_mat.shape

        f = np.arange(NF) * (self.Fs / 2) / NF
        t = np.arange(NT) * 0.010

        plot_xtrogram(t, f, H_mat, self.Fs, kwargs)

    def _resolve_lpc(self, window, M):
        
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

        return gain, a

    def _resolve_lpc_encoding(self, window, kwargs):

        M = kwargs["M"]
        zi = kwargs["zi"]
        N = kwargs["N"]

        gain, a = self._resolve_lpc(window, M)

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

        kwargs["zi"] = zi

        return s

    def _resolve_lpc_trogram(self, window, kwargs):

        M = kwargs["M"]

        gain, a = self._resolve_lpc(window, M)

        # Frequecy from the Filter
        w, h = freqz([1], [1] + list(a*(-1)))

        _H = np.abs(h)*gain
        
        return _H

    def _resolve_ceps(self, window, kwargs):
        
        N = kwargs['N']
        
        # Gets the FFT of the window
        S_win = fft(window, nfft=8*len(window))

        # Gets the cepstrum _s(n) = IFFT(log(|S|))
        _s = ifft(np.log(np.abs(S_win)))

        # Build time filter
        # to remove the x part
        filt = np.zeros(len(_s))

        for i in range(N):
            filt[i] = 1
        for i in range(len(filt)-(N-1), len(filt)):
            filt[i] = 1

        _h = _s * filt

        # Gets the FFT of the _h
        _H = np.abs(np.exp(fft(_h)))
        
        return _H
 
    def get_samples(self):

        return self.x

    def plot(self, which, **kwargs):

        fplot = self.PLOTS[which.lower()]

        fplot(kwargs)

    def fft(self, Nfft=None):

        return fft(self.x, Nfft)

    def convolve(self, s, mode="full"):
        
        x = s.get_samples()

        conv = np.convolve(self.x, x, mode)

        return Signal(conv, self.Fs)

    def export(self, name):

        export(self.x, self.Fs, name)

    def synthesize(self):

        """
            It generates the 'ae' phoneme
        """

        self.Fs = 16000
        Ts = 1/self.Fs
        
        # Source: impulse train
        F0 = 130
        t = np.arange(self.Fs) * Ts
        p = np.zeros(len(t))
        for i in range(len(p)):
            p[i] = 1 if i % F0 == 0 else 0
        
        # Vocal tract model
        Fk_sigmak = np.array([(660, 60),(1720, 100),(2410, 120),(3500, 175),(4500, 250)])
        
        filters = []
        for Fk, sigmak in Fk_sigmak:
            rho = np.exp(-2 * np.pi * sigmak * Ts)
            filters.append(np.array([1, -2* rho * np.cos(2 * np.pi * Fk * Ts), rho**2]))

        V = np.array(filters[0])
        for f in range(1, len(filters)):
            conv = np.convolve(V, filters[f])
            V = conv

        # Lip radiation
        R = np.array([1, -0.96])

        # Final model impulse response
        # s = p * v * r == S(z) = P(z).V(z).R(z)
        self.x = lfilter(R, V, p)
        self.L = np.size(self.x)
        self.t = np.arange(self.L) / self.Fs

    def encode(self, M=20, N=8):

        """
            It uses LPC (Linear Predictive Coding)
        """

        res = sampler(self.x, self.Fs, self._resolve_lpc_encoding, M=M, N=N, zi=np.zeros(M-1))

        return res

    def decode(self, samples, M=20):

        """
            It uses LPC (Linear Predictive Coding)
        """

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

    def lpctrogram(self):
        
        H_mat = sampler(self.x, self.Fs, self._resolve_lpc_trogram, M=20)

        return H_mat

    def cepstrogram(self):
        
        H_mat = sampler(self.x, self.Fs, self._resolve_ceps, N=80)
        
        return H_mat


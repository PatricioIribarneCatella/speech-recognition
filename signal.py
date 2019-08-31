import numpy as np

from matplotlib import pyplot as plt
import IPython.display as ipd

from scipy.io.wavfile import read as wavread, write as wavwrite
from scipy.signal import lfilter
from scipy.signal import spectrogram
from scipy.signal import get_window
from scipy.linalg import solve_toeplitz

class Signal:
    
    def __init__(self, x=np.array([]),Fs=1.,t0=0.):
        self.x = x.astype(np.float64) # Valores de la señal
        self.L = np.size(x) #  Largo de la señal
        self.Fs = Fs # Frecuencia de muestreo
        self.t = np.arange(self.L) / self.Fs + t0 # Tiempo sobre el cual se definen los valores

        
        
    """
        Operaciones para crear una señal:
    """
    
    @classmethod
    def from_wav(cls, filename):
        """
            Lee un wav que puede estar en formato int16, int32, float32, float64 o uint8 y devuelve
            una instancia de Signal() cuyo vector x siempre es de tipo np.float64 y tiene valores 
            entre -1 y 1. 
        """
        
        Fs, x = wavread(filename)
        
        if x.dtype == 'int16':
            nb_bits = np.float(16)
        elif x.dtype == 'int32':
            nb_bits = np.float(32)
        elif x.dtype == 'float32':
            return cls(x.astype(np.float),Fs,0)
        elif x.dtype == 'float64':
            return cls(x.astype(np.float),Fs,0)
        elif x.dtype == 'uint8':
            x = x / 2**8
            return cls(x.astype(np.float),Fs,0)
        else:
            print('No se puede leer el archivo WAV. El formato de cuantización no está soportado por la función scipy.io.wavfile.read')
            return        
        
        x = x / 2**(nb_bits-1)
        return cls(x.astype(np.float),Fs,0)
    

    def fft(self,Nfft=0):
        """
            Función para calcular la DFT normalizada de la señal.
        """
        if Nfft <= 0:
            Nfft = self.L
        return np.fft.fft(self.x,Nfft)


    def spectrogram(self, ax=None, window='hanning', t_window=.025, t_overlap=0., 
                    Nfft=None, detrend='constant', return_onesided=True, scaling='density', 
                    axis=-1, mode='psd'):
        
        n_perseg = int(t_window * self.Fs)
        n_overlap = int(t_overlap * self.Fs)
        if Nfft is None:
            Nfft = n_perseg * 8
        
        f, t, Sxx = spectrogram(self.x, window=window, fs=self.Fs, nperseg=n_perseg, 
                                noverlap=n_overlap, nfft=Nfft, detrend=detrend, 
                                return_onesided=return_onesided, scaling=scaling, 
                                axis=axis, mode=mode)
        if ax is None:
            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)
        ax.pcolormesh(t,f,np.log(np.abs(Sxx)))
        ax.set_xlabel('t [seg]')
        ax.set_ylabel('F [Hz]')
        
        return ax        
        
        
    def play(self):
        """
            Muestra la barra de audio para escuchar la señal.
        """
        return ipd.Audio(self.x, rate=self.Fs)

    
    def to_wav(self,filename):
        """
            Escribe la señal en un archivo .wav
        """
                
        wavwrite(filename,self.Fs,self.x)


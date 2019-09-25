[x, Fs] = audioread("waves/synt.wav");

S = fft(x);
freq = (0:(1/(length(S)-1)):1) .* (Fs/2);
%plot(freq, abs(S))

_s = ifft(log(abs(S)));
t = (0:length(_s)-1)/Fs;
%plot(t, _s)

N = 80;
filt = zeros(length(_s),1);
filt(1:N) = 1;
filt((end-(N-1)):end) = 1;
%plot(t, filt)

_h = _s .* filt;
%plot(t, _h)

_H = fft(_h);
_H = exp(_H);
%plot(freq, abs(_H)./max(abs(_H)))

plot(freq, abs(_H)./max(abs(_H)), 'r', freq, abs(S)./max(abs(S)), 'b')

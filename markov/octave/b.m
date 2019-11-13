function[res] = b(y, mu, sig)
    res = mvnpdf(y, mu, sig);
end

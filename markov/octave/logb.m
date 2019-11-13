function[prob] = logb(x, mu, sig)
  prob = -log(2*pi) - 0.5*log(det(sig)) - (0.5)*(x-mu)'*inv(sig)*(x-mu);
end

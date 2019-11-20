a = hmm1.trans;
a(a == 0) = 1E-100;
trans = log(a);

[alphamat, alphalogp] = alpha(X1, trans, hmm1.means, hmm1.vars);
[betamat, betalogp] = beta(X1, trans, hmm1.means, hmm1.vars);

gammas = calcgamma(alphamat, betamat, length(X1));
ximat = calcxi(X1, alphamat, betamat, alphalogp, trans, hmm1.means, hmm1.vars);


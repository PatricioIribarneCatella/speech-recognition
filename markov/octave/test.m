a = hmm1.trans;
a(a == 0) = 1E-200;
trans = log(a);

N = 3;

[alphamat, alphalogp] = alpha(X1, trans, hmm1.means, hmm1.vars);
[betamat, betalogp] = beta(X1, trans, hmm1.means, hmm1.vars);

gammas = calcgamma(alphamat, betamat, N);
ximat = calcxi(X1, alphamat, betamat, alphalogp, trans, hmm1.means, hmm1.vars);


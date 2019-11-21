a = hmm1.trans;
a(a == 0) = 1E-100;
trans = log(a);

X = X1;

[alphamat, alphalogp] = alpha(X, trans, hmm1.means, hmm1.vars);
[betamat, betalogp] = beta(X, trans, hmm1.means, hmm1.vars);

gammas = calcgamma(alphamat, betamat);
ximat = calcxi(X, alphamat, betamat, alphalogp, trans, hmm1.means, hmm1.vars);

newtrans = calctrans(ximat, gammas);
newmeans = calcmu(X, gammas);
newsigmas = calcsigma(X, gammas, newmeans);


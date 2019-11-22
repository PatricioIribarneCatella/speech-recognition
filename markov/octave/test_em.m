
X = X1;
means = hmm1.means;
sigmas = hmm1.vars;
a = hmm1.trans;

[newmeans, newsigmas, gammas, trans, it] = em(X, means, sigmas, a);


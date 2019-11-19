function[newmeans, newsigmas, gammas, trans] = em(X, means, sigmas, a)

	% initialize variables
	N = 3;
	a(a == 0) = 1E-200;
	trans = log(a);
	newmeans = means;
	newsigmas = sigmas;

	[alphamat, alphalogprob] = alpha(X, trans, newmeans, newsigmas);
	[betamat, betalogprob] = beta(X, trans, newmeans, newsigmas);

	%%%%%%%%%%%%%%%%
	%%%% E step %%%%
	%%%%%%%%%%%%%%%%
	
	gammas = calcgamma(alphamat, betamat, N);

	%%%%%%%%%%%%%%%%
	%%%% M step %%%%
	%%%%%%%%%%%%%%%%

	newmeans = calcmu(X, gammas);
	newsigmas = calcsigma(X, gammas, newsigmas);
	newxi = calcxi(X, alphamat, betamat, alphalogprob, trans, newmeans, newsigmas);
	trans = calctrans(newxi, gammas);
end

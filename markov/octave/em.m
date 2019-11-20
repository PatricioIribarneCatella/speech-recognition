function[newmeans, newsigmas, gammas, trans, it] = em(X, means, sigmas, a)

	% initialize variables
	N = 3;
	it = 0;

	a(a == 0) = 1E-200;
	trans = log(a);
	
	newmeans = means;
	newsigmas = sigmas;
	
	L = zeros(1,2);
	L(2) = calcl(X, newmeans, newsigmas);
	deltaL = L(2) - L(1);

	while abs(deltaL) > 0.01
		
		[alphamat, alphalogprob] = alpha(X, trans, newmeans, newsigmas);
		[betamat, betalogprob] = beta(X, trans, newmeans, newsigmas);

		%%%%%%%%%%%%%%%%
		%%%% E step %%%%
		%%%%%%%%%%%%%%%%
		
		gammas = calcgamma(alphamat, betamat, N);
		ximat = calcxi(X, alphamat, betamat, alphalogprob, trans, newmeans, newsigmas);

		%%%%%%%%%%%%%%%%
		%%%% M step %%%%
		%%%%%%%%%%%%%%%%

		newmeans = calcmu(X, gammas);
		newsigmas = calcsigma(X, gammas, newmeans);
		trans = calctrans(ximat, gammas);

		%% update L and iterations
		L(1) = L(2);
		L(2) = calcl(X, newmeans, newsigmas);
		deltaL = L(2) - L(1);
		it++;
	end
end

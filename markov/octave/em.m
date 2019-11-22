function[newmeans, newsigmas, gammas, trans, it] = em(X, means, sigmas, a)

	% initialize variables
	it = 0;

	a(a == 0) = 1E-100;
	trans = log(a);
	
	newmeans = means;
	newsigmas = sigmas;
	
	L = zeros(1,2);
	L(2) = calcl(X, trans, newmeans, newsigmas);
	deltaL = L(2) - L(1);

	while abs(deltaL) > 0.001
		
		printf("Iter: %d\n", it);

		[alphamat, alphalogprob] = alpha(X, trans, newmeans, newsigmas);
		[betamat, betalogprob] = beta(X, trans, newmeans, newsigmas);

		%%%%%%%%%%%%%%%%
		%%%% E step %%%%
		%%%%%%%%%%%%%%%%
		
		gammas = calcgamma(alphamat, betamat);
		ximat = calcxi(X, alphamat, betamat, alphalogprob, trans, newmeans, newsigmas);

		%%%%%%%%%%%%%%%%
		%%%% M step %%%%
		%%%%%%%%%%%%%%%%

		trans = calctrans(ximat, gammas);
		newmeans = calcmu(X, gammas);
		newsigmas = calcsigma(X, gammas, newmeans);

		%% update L and iterations
		L(1) = L(2);
		L(2) = calcl(X, trans, newmeans, newsigmas);
		deltaL = L(2) - L(1);
		it++;
	end
end


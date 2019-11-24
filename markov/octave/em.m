function[newmeans, newsigmas, gammas, trans, it] = em(X, means, sigmas, a)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - X: matrix (dim: 2 x TIME) 		%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	%%
%%  - a: matrix (dim: 5x5) 			%%
%% OUPUT 					%%
%%  - newmeans: cell (dim: 5 x 2-vector) 	%%
%%  - newsigmas: cell (dim: 5 x 2x2-matrix) 	%%
%%  - gammas: matrix (dim: STATES x TIME) 	%%
%%  - trans: matrix (dim: 5x5) 			%%
%%  - it: integer 				%%
%% 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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


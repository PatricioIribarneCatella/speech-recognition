function[HMM, gammas, it] = em(X, means, sigmas, a, ST)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - X: matrix (dim: 2 x TIME) 		%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	%%
%%  - a: matrix (dim: 5x5) 			%%
%% OUPUT 					%%
%%  - HMM: object with the form: 		%%
%%    - HMM.means: cell (dim: 5 x 2-vector) 	%%
%%    - HMM.vars: cell (dim: 5 x 2x2-matrix) 	%%
%%    - HMM.trans: matrix (dim: 5x5) 		%%
%%  - gammas: matrix (dim: STATES x TIME) 	%%
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

		% plotting
		HMM.means = newmeans;
		HMM.vars = newsigmas;
		HMM.trans = exp(trans);
		hfg = figure();
		plotseq2(X, ST, HMM);
		title(sprintf('Observations, Sequence - Iteration: %d - EM model', it));
		saveas(hfg, sprintf("iter-%d.png", it));

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

	HMM.means = newmeans;
	HMM.vars = newsigmas;
	HMM.trans = exp(trans);
end


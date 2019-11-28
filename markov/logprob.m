function [prob] = logprob(X, ST, HMM)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - X: matrix (dim: 2 x TIME) 		%%
%%  - ST: vector (dim: TIME) 			%%
%%  - HMM: object with the form: 		%%
%%    - HMM.means: cell (dim: 5 x 2-vector) 	%%
%%    - HMM.vars: cell (dim: 5 x 2x2-matrix) 	%%
%%    - HMM.trans: matrix (dim: 5x5) 		%%
%% OUPUT 					%%
%%  - prob: double				%%
%% 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	means = HMM.means;
	sigmas = HMM.vars;
	a = HMM.trans;

	a(a == 0) = 1E-100;
	a = log(a);

	N = length(X);
	prob = 0;

	for i = 1:N
		mu = means{ST(i+1)};
		sig = sigmas{ST(i+1)};
		prob += a(ST(i), ST(i+1)) + logb(X(i,:)', mu, sig);
	end

	prob += a(ST(N+1), 5);
end

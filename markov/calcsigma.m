function[res] = calcsigma(X, gammas, means)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - X: matrix (dim: 2 x TIME) 		%%
%%  - gammas: matrix (dim: STATES x TIME) 	%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%% OUPUT 					%%
%%  - res: cell (dim: 5 x 2x2-matrix) 		%%
%% 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	sigmas = {};
	den = calcden(gammas);
	N = size(gammas)(1);

	sigmas{1} = [];

	for k = 1:N
		
		aux = zeros(2, 2);
		
		for t = 1:length(X)
			xminm = X(t,:)' - means{k+1};
			aux += exp(gammas(k, t)) .* (xminm * xminm');
		end
		
		sigmas{k+1} = aux ./ exp(den(k));
	end

	sigmas{5} = [];

	res = sigmas;
end


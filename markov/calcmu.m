function [res] = calcmu(X, gammas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - X: matrix (dim: 2 x TIME) 		%%
%%  - gammas: matrix (dim: STATES x TIME) 	%%
%% OUPUT 					%%
%%  - res: cell (dim: 5 x 2-vector) 		%%
%% 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	means = {};
	den = calcden(gammas);
	N = size(gammas)(1);

	means{1} = [];

	for k = 1:N
	
		aux = zeros(2, 1);
	
		for t = 1:length(X)
			aux += exp(gammas(k, t)) .* X(t,:)';
		end
	
		means{k+1} = aux ./ exp(den(k));
	end

	means{5} = [];

	res = means;
end


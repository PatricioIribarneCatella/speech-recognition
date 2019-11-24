function [res] = calcden(gammas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - gammas: matrix (dim: STATES x TIME) 	%%
%% OUPUT 					%%
%%  - res: vector (dim: STATES) 		%%
%% 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	N = size(gammas)(1);

	res = zeros(1, N);

	for k = 1:N
		res(k) = logsum(gammas(k,:));
	end
end


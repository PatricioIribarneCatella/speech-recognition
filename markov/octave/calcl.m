function [L] = calcl(X, trans, means, sigmas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - X: matrix (dim: 2 x TIME) 		%%
%%  - trans: matrix (dim: 5x5) 			%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	%%
%% OUPUT 					%%
%%  - L: double 				%%
%% 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	[_, L] = alpha(X, trans, means, sigmas);
end


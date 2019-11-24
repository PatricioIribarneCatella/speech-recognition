function[res] = calcxi(X, alphamat, betamat, logprob, a, means, sigmas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						 %%
%% INPUT 					 %%
%%  - X: matrix (dim: 2 x TIME) 		 %%
%%  - alphamat: matrix (dim: STATES x TIME) 	 %%
%%  - betamat: matrix (dim: STATES x TIME) 	 %%
%%  - logprob: double 				 %%
%%  - a: matrix (dim: 5x5) 			 %%
%%  - means: cell (dim: 5 x 2-vector) 		 %%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	 %%
%% OUPUT 					 %%
%%  - res: 3D-matrix (dim: 5 x 5 x TIME) 	 %%
%% 						 %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	ximat = zeros(5, 5, length(X));
	aux = zeros(1, 3);

	for t = 2:length(X)
		
		logden = logsum(alphamat(:, t) + betamat(:,t));

		for j = 2:4
			for k = 2:4
				b = logb(X(t,:)', means{k}, sigmas{k});
				ximat(j,k,t) = alphamat(j-1, t-1) + a(j,k) + b + betamat(k-1, t) - logden;
			end
		end
	end

	res = ximat;
end


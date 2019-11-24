function [mat] = calcgamma(alphamat, betamat)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						 %%
%% INPUT 					 %%
%%  - alphamat: matrix (dim: STATES x TIME) 	 %%
%%  - betamat: matrix (dim: STATES x TIME) 	 %%
%% OUPUT 					 %%
%%  - mat: matrix (dim: STATES x TIME) 		 %%
%% 						 %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	mat = alphamat .+ betamat;

	for i = 1:length(alphamat)
		aux = logsum(mat(:,i));
		mat(:,i) = mat(:,i) - aux;
	end
end


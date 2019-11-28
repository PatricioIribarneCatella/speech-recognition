function[mat, logprob] = alpha(Y, a, means, sigmas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						%%
%% INPUT 					%%
%%  - Y: matrix (dim: 2 x TIME) 		%%
%%  - a: matrix (dim: 5x5) 			%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	%%
%% OUPUT 					%%
%%  - mat: matrix (dim: STATES x TIME) 		%%
%%  - logprob: double 				%%
%% 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	T = length(Y);
	N = 3;

	alpham = zeros(N, T);

	% initialize alpha matrix
	for j = 1:N
		alpham(j, 1) = a(1, j+1) + logb(Y(1,:)', means{j+1}, sigmas{j+1});
	end

	% continue with following values
	for t = 2:T
	
		for j = 1:N
		
			aux = zeros(1,N);
			
			for i = 1:N
				aux(i) = a(i+1,j+1) + alpham(i, t-1);
			end
			
			logaux = logsum(aux);
			alpham(j, t) = logb(Y(t,:)', means{j+1}, sigmas{j+1}) + logaux;
		end
	end

	% finish the last values
	logprob = logsum(alpham(:,T) + a(2:4,5));
	mat = alpham;
end


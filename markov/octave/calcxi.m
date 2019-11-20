function[res] = calcxi(X, alphamat, betamat, logprob, a, means, sigmas)

	ximat = zeros(5, 5, length(X));
	aux = zeros(1, 3);

	for t = 2:length(X)
		
		for k = 1:3
			aux(k) = logb(X(t,:)', means{k+1}', sigmas{k+1});
		end
		
		aux = aux .+ betamat(:, t)';
		
		for j = 2:4
			ximat(j,2:4,t) = (a(j,2:4) .+ aux) + alphamat(j-1,t-1) - logprob;
		end
	end

	res = ximat;
end

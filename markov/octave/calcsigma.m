function[res] = calcsigma(X, gammas, means)

	sigmas = {};
	den = calcden(gammas);

	sigmas{1} = zeros(2,2);

	for k = 1:3
		
		aux = zeros(2,2);
		
		for t = 1:length(X)
			xminm = X(t,:)' - means{k+1};
			aux += exp(gammas(k,t)) .* (xminm * xminm');
		end
		
		sigmas{k+1} = aux ./ exp(den(k));
	end

	sigmas{5} = zeros(2,2);

	res = sigmas;
end

function[res] = calcsigma(X, gammas, means)

    sigmas = {};
    den = calcden(gammas);

    for k = 1:3
        aux = zeros(2,2);
        for t = 1:length(X)
	    xminm = X(t,:)' - means{k};
	    aux += exp(gammas(k,t)) .* (xminm * xminm');
	end
	sigmas{k} = aux ./ exp(den(k));
    end

    res = sigmas;
end

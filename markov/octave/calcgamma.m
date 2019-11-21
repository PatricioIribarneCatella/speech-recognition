function[mat] = calcgamma(alphamat, betamat)

	mat = alphamat .+ betamat;

	for i = 1:length(alphamat)
		aux = logsum(mat(:,i));
		mat(:,i) = mat(:,i) - aux;
	end
end

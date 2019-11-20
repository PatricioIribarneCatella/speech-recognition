function[mat] = calcgamma(alphamat, betamat, N)

	mat = alphamat .+ betamat;

	for i = 1: N
		aux = logsum(mat(:,i));
		mat(:,i) = mat(:,i) - aux;
	end
end

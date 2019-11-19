function[res] = calcden(gammas)

	res = zeros(1,3);

	for k = 1:3
		res(k) = logsum(gammas(k,:));
	end

end

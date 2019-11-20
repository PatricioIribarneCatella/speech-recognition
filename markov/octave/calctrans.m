function[res] = calctrans(xi, gammas)

	den = calcden(gammas);

	trans(1:5, 1:5) = -460;

	% starts the matrix with a '1' (log(1) = 0)
	% in the a(1,2) position to make
	% the sequence starts, and a '1' (log(1) = 0)
	% in the last position to finish
	% the sequence
	trans(1,2) = 0;
	trans(5,5) = 0;

	% complete the 'trans' matrix center
	% by summing up all the centers
	% in the 'xi' matrix
	for j = 2:4
		for k = 2:4
			trans(j,k) = logsum(xi(j,k,2:end));
		end
	end

	% complete the 'trans' matrix
	% by dividing the rows by
	% the denominator (substract in log calc)
	% and calc the last column (1 - sum(trans(j,2:4))),
	% but in log calc its:
	%  logsum([0, -trans(j,2), -trans(j,3), -trans(j,4)])

	aux = zeros(1,4);

	for j = 2:4
		trans(j,2:4) = trans(j,2:4) - den(j-1);
		aux(2:4) = -1 * trans(j,2:4);
		trans(j,5) = logsum(aux);
	end

	res = trans;
end

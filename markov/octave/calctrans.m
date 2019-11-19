function[res] = calctrans(xi, gammas)

	den = calcden(gammas);

	trans = zeros(5,5);
	trans(trans == 0) = -200;

	% starts the matrix with a '1' (log(1) = 0)
	% in the a(1,2) position to make
	% the sequence starts, and a '1' (log(1) = 0)
	% in the last position to finish
	% the sequence
	trans(1,2) = 0;
	trans(5,5) = 0;

	for j = 2:4
		for k = 2:4
			trans(j,k) = logsum(xi(j,k,:));
		end
	end

	% complete the 'a' matrix
	% by dividing the rows by
	% the denominator, and calc
	% the last column

	aux = zeros(1,4);

	for j = 2:4
		trans(j,2:4) = trans(j,2:4) - den(j-1);
		aux(2:4) = -1 * trans(j,2:4);
		trans(j,5) = logsum(aux);
	end

	res = trans;
end

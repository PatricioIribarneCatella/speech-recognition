function[res] = calcden(gammas)

    res = zeros(1,3);

    for k = 1:3
        for t = 1:length(gammas)
            res(k) += gammas(k,t);
	end
    end

end

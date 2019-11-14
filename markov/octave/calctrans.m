function[res] = calctrans(xi, gammas)

    den = calcden(gammas);

    for t = 2:length(gammas)
        a(j,k) += xi(t, j, k);
    end

end

function[res] = calctrans(xi, gammas)

    den = calcden(gammas);

    trans = zeros(5,5);

    for t = 2:length(gammas)
        trans += xi(t,:,:);
    end

end

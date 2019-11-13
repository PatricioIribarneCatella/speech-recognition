function[mat] = gammal(alpha, beta, N)

    mat = alpha .+ beta;

    for i = 1: N
        aux = logsum(mat(:,i));
        mat(:,i) = mat(:,i) ./ aux;
    end
end

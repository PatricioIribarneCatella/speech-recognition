function[res]=alpha(Y, a, means, sigmas, N, T)

    % it only contains the
    % previous state and
    % the current state
    alpham = zeros(N, 2);

    % initialize alpha matix
    for j = 1:N
        alpham(j, 1) = a(1, j+1) + log_b(Y(1,:)', means{j+1}, sigmas{j+1});
    end
    
    % continue with following values
    for t = 2:T
        for j = 1:N
            aux = 0;
            for i = 1:N
                aux += log_b(Y(t,:)', means{j+1}, sigmas{j+1}) + a(i+1,j+1) + alpham(i, 1);
            end
            alpham(j, 2) = aux;
        end
    end

    res = alpham;
end

function[mat, logprob] = beta(Y, a, means, sigmas)

    T = length(Y);
    N = 3;

    betam = zeros(N, T);

    % initialize beta matrix
    betam(:, T) = a(2:4,5);
    
    % continue with the following values
    for t = T-1:-1:1
        for i = 1:N
            aux = zeros(1,N);
            for j = 1:N
                aux(j) = logb(Y(t+1,:)', means{j+1}, sigmas{j+1}) + a(i+1,j+1) + betam(j, t+1);
            end
            betam(i,t) = logsum(aux);
        end
    end
    
    % calc the log-prob
    aux = zeros(1,N);
    
    for i = 1:N
        aux(i) = betam(i,1) + a(1,i+1) + logb(Y(1,:)', means{i+1}, sigmas{i+1});
    end
    
    logprob = logsum(aux);
    mat = betam;
end

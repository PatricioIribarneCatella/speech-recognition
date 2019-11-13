function[mat, logprob]=alpha(Y, a, means, sigmas, N, T)

    % it only contains the
    % previous state and
    % the current state
    alpham = zeros(N, 2);

    % initialize alpha matrix
    for j = 1:N
        alpham(j, 1) = a(1, j+1) + log_b(Y(1,:)', means{j+1}, sigmas{j+1});
    end
    
    % continue with following values
    for t = 2:T
        for j = 1:N
            aux = zeros(1,N);
            for i = 1:N
                aux(i) = a(i+1,j+1) + alpham(i, 1);
            end
            logaux = logsum(aux);
            alpham(j, 2) = log_b(Y(t,:)', means{j+1}, sigmas{j+1}) + logaux;
        end
        alpham(:,1) = alpham(:,2);
    end

    % finish the last values
    logprob = logsum(alpham(:,2) + a(2:4,5));
    mat = alpham;
end

%=================================
function result = logsum(logv)

    len = length(logv);
    if (len<2);
      error('Subroutine logsum cannot sum less than 2 terms.');
    end;

    % First two terms
    if (logv(2)<logv(1)),
      result = logv(1) + log( 1 + exp( logv(2)-logv(1) ) );
    else,
      result = logv(2) + log( 1 + exp( logv(1)-logv(2) ) );
    end;

    % Remaining terms
    for (i=3:len),
      term = logv(i);
      if (result<term),
        result = term   + log( 1 + exp( result-term ) );
      else,
        result = result + log( 1 + exp( term-result ) );
      end;    
    end;
end
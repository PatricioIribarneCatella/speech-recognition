function[res] = calcmu(X, gammas)

   means = {};
   den = calcden(gammas);

   means{1} = zeros(1,2);

   for k = 1:3
       aux = zeros(1,2);
       for t = 1:length(X)
           aux += exp(gammas(k, t)) .* X(t,:);
       end
       means{k+1} = aux ./ exp(den(k));
   end

   means{5} = zeros(1,2);

   res = means;
end

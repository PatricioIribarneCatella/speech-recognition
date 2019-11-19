function[res] = calcmu(X, gammas)

   means = {};
   den = calcden(gammas);

   for k = 1:3
       aux = zeros(1,2);
       for t = 1:length(X)
           aux += exp(gammas(k, t)) .* X(t,:);
       end
       means{k} = aux ./ exp(den(k));
   end

   res = means;
end

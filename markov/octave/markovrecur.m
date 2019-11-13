models = [hmm1, hmm2, hmm3, hmm4, hmm5, hmm6];
X = {X1, X2, X3, X4, X5, X6};

L = length(X);
Q = 3;

for k = 1:L

    Xk = X{k};

    LH = zeros(1, L);
    
    for m = 1:length(models)

        model = models(m);

        a = model.trans;
        a(a == 0) = 1E-200;
        a = log(a);

        means = model.means;
        sigmas = model.vars;
        
        [alphamat,prob] = alpha(Xk, a, means, sigmas, Q, length(Xk));

        % calc P(Y)
        %for q = 1:Q
        %    prob += alphamat(q, 2);
        %end
        
        LH(m) = prob;
    end
    
    [val,argmax] = max(LH);
    printf("(X, ST): %d -> Model: %d (prob: %f)\n", k, argmax, val);
end
models = [hmm1, hmm2, hmm3, hmm4, hmm5, hmm6];
X = {X1, X2, X3, X4, X5, X6};
ST = {ST1, ST2, ST3, ST4, ST5, ST6};

L = length(X);

for m = 1:length(models)

    model = models(m);

    a = model.trans;
    a(a == 0) = 1E-200;
    a = log(a);

    LH = zeros(1, L);

    for k = 1:L

        Xk = X{k};
        STk = ST{k};

        N = length(Xk);
        prob = 0;

        for i = 1:N
            mu = model.means{STk(i+1)};
            sig = model.vars{STk(i+1)};
            prob += a(STk(i), STk(i+1)) + log_b(Xk(i,:)', mu, sig);
        end

        prob += a(STk(N+1), 5);
        LH(k) = prob;
    end
    disp(LH);

    [val,argmax] = max(LH);
    printf("Model: %d, Prob: %f, X: %d\n", m, val, argmax);  
end

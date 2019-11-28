models = [hmm1, hmm2, hmm3, hmm4, hmm5, hmm6];
X = {X1, X2, X3, X4, X5, X6};
ST = {ST1, ST2, ST3, ST4, ST5, ST6};

L = length(X);

for k = 1:L

	Xk = X{k};
	STk = ST{k};

	LH = zeros(1, L);

	for m = 1:length(models)

		model = models(m);

		LH(m) = logprob(Xk, STk, model);
	end

	[val, argmax] = max(LH);
	
	printf("(X, ST): %d -> Model: %d (prob: %f)\n", k, argmax, val);
end


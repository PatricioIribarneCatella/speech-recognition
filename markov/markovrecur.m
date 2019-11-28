models = [hmm1, hmm2, hmm3, hmm4, hmm5, hmm6];
X = {X1, X2, X3, X4, X5, X6};

L = length(X);

for k = 1:L

	Xk = X{k};

	LH = zeros(1, L);

	for m = 1:length(models)

		model = models(m);

		a = model.trans;
		means = model.means;
		sigmas = model.vars;

		a(a == 0) = 1E-100;
		a = log(a);

		[_, prob] = alpha(Xk, a, means, sigmas);

		LH(m) = prob;
	end

	[val, argmax] = max(LH);

	printf("(X, ST): %d -> Model: %d (prob: %f)\n", k, argmax, val);
end


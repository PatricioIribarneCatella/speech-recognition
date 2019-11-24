% create a new sequence from HMM4 with at least
% fifteen or more observations in each state

done = false;

while !done
	[X, ST] = genhmm(hmm4);
	done = length(ST(ST == 2)) >= 15 && ...
		length(ST(ST == 3)) >= 15 && ...
		length(ST(ST == 4)) >= 15;
end

% generate first means
m = mean(X)';
means = {[], m, m, m, []};

% generate first sigmas
sig = cov(X);
sigmas = {[], sig, sig, sig, []};

% generate first transition matrix
a = [0 1 0 0 0; 0 0.5 0.5 0 0; 0 0 0.5 0.5 0; 0 0 0 0.5 0.5; 0 0 0 0 1];

[newmeans, newsigmas, gammas, trans, it] = em(X, means, sigmas, a);


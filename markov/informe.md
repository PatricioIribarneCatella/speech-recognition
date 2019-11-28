# HMM: Hidden Markov Models y Viterbi

Procesamiento del Habla (66.46) - _FIUBA_

## Algoritmos

- **EM**

```octave
function[HMM, gammas, it] = em(X, means, sigmas, a, ST)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 												%%
%% INPUT 										%%
%%  - X: matrix (dim: 2 x TIME) 				%%
%%  - means: cell (dim: 5 x 2-vector) 			%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 		%%
%%  - a: matrix (dim: 5x5) 						%%
%% OUPUT 										%%
%%  - HMM: object with the form: 				%%
%%    - HMM.means: cell (dim: 5 x 2-vector) 	%%
%%    - HMM.vars: cell (dim: 5 x 2x2-matrix) 	%%
%%    - HMM.trans: matrix (dim: 5x5) 			%%
%%  - gammas: matrix (dim: STATES x TIME) 		%%
%%  - it: integer 								%%
%% 												%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	% initialize variables
	it = 0;

	a(a == 0) = 1E-100;
	trans = log(a);
	
	newmeans = means;
	newsigmas = sigmas;
	
	L = zeros(1,2);
	L(2) = calcl(X, trans, newmeans, newsigmas);
	deltaL = L(2) - L(1);

	while abs(deltaL) > 0.001
		
		printf("Iter: %d\n", it);

		% plotting
		HMM.means = newmeans;
		HMM.vars = newsigmas;
		HMM.trans = exp(trans);
		hfg = figure();
		plotseq2(X, ST, HMM);
		title(sprintf('Observations, Sequence - Iteration: %d - EM model', it));
		saveas(hfg, sprintf("iter-%d.png", it));

		[alphamat, alphalogprob] = alpha(X, trans, newmeans, newsigmas);
		[betamat, betalogprob] = beta(X, trans, newmeans, newsigmas);

		%%%%%%%%%%%%%%%%
		%%%% E step %%%%
		%%%%%%%%%%%%%%%%
		
		gammas = calcgamma(alphamat, betamat);
		ximat = calcxi(X, alphamat, betamat, alphalogprob, trans, newmeans, newsigmas);

		%%%%%%%%%%%%%%%%
		%%%% M step %%%%
		%%%%%%%%%%%%%%%%

		trans = calctrans(ximat, gammas);
		newmeans = calcmu(X, gammas);
		newsigmas = calcsigma(X, gammas, newmeans);

		%% update L and iterations
		L(1) = L(2);
		L(2) = calcl(X, trans, newmeans, newsigmas);
		deltaL = L(2) - L(1);
		it++;
	end

	HMM.means = newmeans;
	HMM.vars = newsigmas;
	HMM.trans = exp(trans);
end
```

- **Alpha**

```octave
function[mat, logprob] = alpha(Y, a, means, sigmas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 											%%
%% INPUT 									%%
%%  - Y: matrix (dim: 2 x TIME) 			%%
%%  - a: matrix (dim: 5x5) 					%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	%%
%% OUPUT 									%%
%%  - mat: matrix (dim: STATES x TIME) 		%%
%%  - logprob: double 						%%
%% 											%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	T = length(Y);
	N = 3;

	alpham = zeros(N, T);

	% initialize alpha matrix
	for j = 1:N
		alpham(j, 1) = a(1, j+1) + logb(Y(1,:)', means{j+1}, sigmas{j+1});
	end

	% continue with following values
	for t = 2:T
	
		for j = 1:N
		
			aux = zeros(1,N);
			
			for i = 1:N
				aux(i) = a(i+1,j+1) + alpham(i, t-1);
			end
			
			logaux = logsum(aux);
			alpham(j, t) = logb(Y(t,:)', means{j+1}, sigmas{j+1}) + logaux;
		end
	end

	% finish the last values
	logprob = logsum(alpham(:,T) + a(2:4,5));
	mat = alpham;
end
```

- **Beta**

```octave
function[mat, logprob] = beta(Y, a, means, sigmas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 											%%
%% INPUT 									%%
%%  - Y: matrix (dim: 2 x TIME) 			%%
%%  - a: matrix (dim: 5x5) 					%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	%%
%% OUPUT 									%%
%%  - mat: matrix (dim: STATES x TIME) 		%%
%%  - logprob: double 						%%
%% 											%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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
				aux(j) = logb(Y(t+1,:)', means{j+1}, sigmas{j+1}) + ...
							a(i+1,j+1) + betam(j, t+1);
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
```

- **Gamma**

```octave
function [mat] = calcgamma(alphamat, betamat)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						 						%%
%% INPUT 					 					%%
%%  - alphamat: matrix (dim: STATES x TIME) 	%%
%%  - betamat: matrix (dim: STATES x TIME) 	 	%%
%% OUPUT 					 					%%
%%  - mat: matrix (dim: STATES x TIME) 		 	%%
%% 						 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	mat = alphamat .+ betamat;

	for i = 1:length(alphamat)
		aux = logsum(mat(:,i));
		mat(:,i) = mat(:,i) - aux;
	end
end
```

- **Xi**

```octave
function[res] = calcxi(X, alphamat, betamat, logprob, a, means, sigmas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 						 						%%
%% INPUT 					 					%%
%%  - X: matrix (dim: 2 x TIME) 		 		%%
%%  - alphamat: matrix (dim: STATES x TIME) 	%%
%%  - betamat: matrix (dim: STATES x TIME) 	 	%%
%%  - logprob: double 				 			%%
%%  - a: matrix (dim: 5x5) 			 			%%
%%  - means: cell (dim: 5 x 2-vector) 		 	%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	 	%%
%% OUPUT 					 					%%
%%  - res: 3D-matrix (dim: 5 x 5 x TIME) 	 	%%
%% 						 						%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	ximat = zeros(5, 5, length(X));
	aux = zeros(1, 3);

	for t = 2:length(X)
		
		logden = logsum(alphamat(:, t) + betamat(:,t));

		for j = 2:4
			for k = 2:4
				b = logb(X(t,:)', means{k}, sigmas{k});
				ximat(j,k,t) = alphamat(j-1, t-1) + a(j,k) + b + betamat(k-1, t) - logden;
			end
		end
	end

	res = ximat;
end
```

- **Mu**

```octave
function [res] = calcmu(X, gammas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 											%%
%% INPUT 									%%
%%  - X: matrix (dim: 2 x TIME) 			%%
%%  - gammas: matrix (dim: STATES x TIME) 	%%
%% OUPUT 									%%
%%  - res: cell (dim: 5 x 2-vector) 		%%
%% 											%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	means = {};
	den = calcden(gammas);
	N = size(gammas)(1);

	means{1} = [];

	for k = 1:N
	
		aux = zeros(2, 1);
	
		for t = 1:length(X)
			aux += exp(gammas(k, t)) .* X(t,:)';
		end
	
		means{k+1} = aux ./ exp(den(k));
	end

	means{5} = [];

	res = means;
end
```

- **Sigmas**

```octave
function[res] = calcsigma(X, gammas, means)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 												%%
%% INPUT 										%%
%%  - X: matrix (dim: 2 x TIME) 				%%
%%  - gammas: matrix (dim: STATES x TIME) 		%%
%%  - means: cell (dim: 5 x 2-vector) 			%%
%% OUPUT 										%%
%%  - res: cell (dim: 5 x 2x2-matrix) 			%%
%% 												%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	sigmas = {};
	den = calcden(gammas);
	N = size(gammas)(1);

	sigmas{1} = [];

	for k = 1:N
		
		aux = zeros(2, 2);
		
		for t = 1:length(X)
			xminm = X(t,:)' - means{k+1};
			aux += exp(gammas(k, t)) .* (xminm * xminm');
		end
		
		sigmas{k+1} = aux ./ exp(den(k));
	end

	sigmas{5} = [];

	res = sigmas;
end
```

- **Matriz de transición**

```octave
function[res] = calctrans(xi, gammas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 												%%
%% INPUT 										%%
%%  - xi: 3D-matrix (dim: 5 x 5 x TIME) 		%%
%%  - gammas: matrix (dim: STATES x TIME) 		%%
%% OUPUT 										%%
%%  - res: matrix (dim: 5 x 5) 					%%
%% 												%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	den = calcden(gammas);

	trans(1:5, 1:5) = -250;

	% starts the matrix with a '1' (log(1) = 0)
	% in the a(1,2) position to make
	% the sequence starts, and a '1' (log(1) = 0)
	% in the last position to finish
	% the sequence
	trans(1,2) = 0;
	trans(5,5) = 0;

	% complete the 'trans' matrix center
	% by summing up all the centers
	% in the 'xi' matrix
	for j = 2:4
		for k = 2:4
			trans(j,k) = logsum(xi(j,k,2:end));
		end
	end

	% complete the 'trans' matrix
	% by dividing the rows by
	% the denominator (substract, in log calc)
	for j = 2:4
		trans(j,2:4) = trans(j,2:4) - den(j-1);
	end

	% and calc the last column (1 - sum(trans(j,2:4))),
	% by applying the exp() function to the inner matrix
	% exp(trans(2:4,2:4))
	exptrans = exp(trans(2:4,2:4));
	for j = 2:4
		r = abs(1.0 - sum(exptrans(j-1,:)));
		if r == 0.0
			trans(j,5) = -250;
		else
			trans(j,5) = log(r);
		end
	end

	res = trans;
end
```

- _Denominador_

```octave
function [res] = calcden(gammas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 											%%
%% INPUT 									%%
%%  - gammas: matrix (dim: STATES x TIME) 	%%
%% OUPUT 									%%
%%  - res: vector (dim: STATES) 			%%
%% 											%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	N = size(gammas)(1);

	res = zeros(1, N);

	for k = 1:N
		res(k) = logsum(gammas(k,:));
	end
end
```

- _Likelihood_

```octave
function [L] = calcl(X, trans, means, sigmas)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% 											%%
%% INPUT 									%%
%%  - X: matrix (dim: 2 x TIME) 			%%
%%  - trans: matrix (dim: 5x5) 				%%
%%  - means: cell (dim: 5 x 2-vector) 		%%
%%  - sigmas: cell (dim: 5 x 2x2-matrix) 	%%
%% OUPUT 									%%
%%  - L: double 							%%
%% 											%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

	[_, L] = alpha(X, trans, means, sigmas);
end
```



## HMM

### Script

```octave
inic_hmm;

% create a new sequence from HMM4 with at least
% fifteen or more observations in each state

done = false;

while ~done
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

[hmmEM, gammas, it] = em(X, means, sigmas, a, ST);

% plot the sequences and its ellipsis for
% the original model and the EM model
hfg = figure('Name','Original model','NumberTitle','off');
plotseq2(X, ST, hmm4);
title('Observations, Sequence - Original model');
saveas(hfg, "original-model.png");

hfg = figure('Name','EM model','NumberTitle','off');
plotseq2(X, ST, hmmEM);
title('Observations, Sequence - EM model');
saveas(hfg, "EM-model.png");
```

### Plots

![Iteración 0](plots/iter-0.png)

![Iteración 1](plots/iter-1.png)

![Iteración 2](plots/iter-2.png)

![Iteración 3](plots/iter-3.png)

![Iteración 4](plots/iter-4.png)

### Comparación

![Modelo **original**](plots/original-model.png)

![Modelo **EM**](plots/EM-model.png)

## Viterbi

### Script

```octave
inic_hmm;

% the following models are used: hmm4 and hmm6

% MEANS
HMM.means = {[],
	hmm4.means{2},
	hmm4.means{3},
	hmm4.means{4},
	hmm6.means{2},
	hmm6.means{3},
	hmm6.means{4},
	[]};

% SIGMAS
HMM.vars = {[],
	hmm4.vars{2},
	hmm4.vars{3},
	hmm4.vars{4},
	hmm6.vars{2},
	hmm6.vars{3},
	hmm6.vars{4},
	[]};

% TRANSITION MATRIX
HMM.trans = zeros(8,8);
HMM.trans(1,2) = HMM.trans(1,5) = 0.5;
HMM.trans(2:4,2:4) = hmm4.trans(2:4,2:4);
HMM.trans(5:7,5:7) = hmm6.trans(2:4,2:4);
HMM.trans(4,2) = HMM.trans(4,5) = HMM.trans(4,8) = hmm4.trans(4,5)/3.0;
HMM.trans(7,2) = HMM.trans(7,5) = HMM.trans(7,8) = hmm6.trans(4,5)/3.0;
HMM.trans(8,8) = 1;

% generate observations and real sequence
% with the big model
[X, ST] = genhmm(HMM);

% computes the estimated sequence
% with VITERBI algorithm
[_ST, _P] = logvit(X, HMM);

% plots the compare between the
% two sequence: original and Viterbi
hfg = figure('Name','Compare: Original vs Viterbi','NumberTitle','off');
compseq(X, ST, _ST);
title('Compare sequences: Original vs Viterbi');
saveas(hfg, "seq-orig-viterbi.png");
clc;

% compare probabilities
% - real: P(X/Zv; M) - it uses the real sequence: ST
% - opt:  P(X/~Z; M) - it uses the VITERBI sequence: _ST
% - tot:  P(X; M) - it uses the logfwd algorithm
%
% 	P(X/Zv; M) <= P(X/~Z; M) <= P(X; M)
%
printf("real: %f\n", logprob(X, ST, HMM));
printf("opt: %f\n", logprob(X, _ST, HMM));
printf("tot: %f\n", logfwd(X, HMM));

% decode the sequence into models
printf("Sequence of models: ");

_STr = _ST(2:end-1);

% puts zeros in the starts of
% the sequences for each model
hmm4_idx = _STr - 2;
hmm6_idx = _STr - 5;

% all the other values are put
% to negative values
hmm4_idx = abs(hmm4_idx) * -1;
hmm6_idx = abs(hmm6_idx) * -1;

% only where there are zeros
% (where each model begins), puts
% the identifier of each model
hmm4_idx(hmm4_idx == 0) = 4;
hmm6_idx(hmm6_idx == 0) = 6;

% where there are negative values
% convert them to ones
hmm4_idx(hmm4_idx < 0) = 1;
hmm6_idx(hmm6_idx < 0) = 1;

% multiply both arrays (value by value)
% so the resulting array contains all
% the sequence, for example:
%   [6 6 6 6 0 0 0 4 4 4 4 0 0 6 6 6 0 0]
tot = hmm4_idx .* hmm6_idx;
tot(tot == 1) = 0;

idx = 1;

while idx < length(tot)

	e = tot(idx);

	if e == 4
		printf("HMM-4 ");
		while e == 4
			e = tot(idx);
			idx++;
		end
	end

	if e == 6
		printf("HMM-6 ");
		while e == 6
			e = tot(idx);
			idx++;
		end
	end

	idx++;
end

printf("\n");
```

### Output

```
real: -5498.833706
opt: -5498.314422
tot: -5497.821365
Sequence of models: HMM-6 HMM-4 HMM-4 HMM-6 HMM-4 HMM-6 HMM-6
```

### Comparación

![Comparación: Original-Viterbi](plots/seq-orig-viterbi.png)



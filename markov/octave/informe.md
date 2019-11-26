# HMM: Hidden Markov Models y Viterbi

Procesamiento del Habla (66.46) - _FIUBA_

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

![Iteración 0](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/iter-0.png)

![Iteración 1](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/iter-1.png)

![Iteración 2](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/iter-2.png)

![Iteración 3](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/iter-3.png)

![Iteración 4](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/iter-4.png)

### Comparación

![Modelo **original**](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/original-model.png)

![Modelo **EM**](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/EM-model.png)

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

_STuni = unique(_ST);
idx = 2;

while idx <= length(_STuni)-1

	e = _STuni(idx);

	if e == 2
		printf("HMM-4 ");
	end

	if e == 5
		printf("HMM-6");
	end

	idx += 3;
end

printf("\n");
```

### Comparación

![Comparación: Original-Viterbi](/home/patricio/Documents/FIUBA/Procesamiento del Habla/proc-habla-ejercicios/markov/octave/plots/seq-orig-viterbi.png)




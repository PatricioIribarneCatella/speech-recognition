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
figure('Name','Compare: Original vs Viterbi','NumberTitle','off');
compseq(X, ST, _ST);
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



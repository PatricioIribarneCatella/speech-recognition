
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


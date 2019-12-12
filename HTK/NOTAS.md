# NOTAS HTK

Procesamiento del Habla (66.43) - FIUBA


## Generación del los coeficientes MFCC 

HCopy -A -V -T 1 -C ../config/config.hcopy -S genmfc.train > ../log/hcopy.train.log
HCopy -A -V -T 1 -C ../config/config.hcopy -S genmfc.test > ../log/hcopy.test.log

# Create wlist considering all the prompts: train and test
export LC_CTYPE=ISO_8859_1
echo "AS  sp" > global.ded
cd etc
cat promptsl40.train promptsl40.test | awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > wlistl40

# Dictionary and phonos founded
HDMan -m -w wlistl40 -g global.ded -n monophones+sil -l ../log/hdman.log dictl40 lexicon

# Convert prompts into MLF (words only)
prompts2mlf mlfwords.test promptsl40.test
prompts2mlf mlfwords.train promptsl40.train

# Convert MLF-words into MLF-phones
HLEd -l '*' -d dictl40 -i phones.train mkphones-sp.led mlfwords.train

# Generate intial parameters: {means, vars, transmat}
# (Previously create dirs: {hmm0, hmm1,...,hmm5})
cd modelos
ls ../datos/mfc/train/*/*.mfc > train.scp
HCompV -C ../config/config -f 0.01 -m -S train.scp -M hmm0 hmm0/proto

# Create 'macros' and 'hmmdefs' for proto
../scripts/go.gen-macros hmm0/vFloors hmm0/proto > hmm0/macros
../scripts/go.gen-hmmdefs ../etc/monophones+sil hmm0/proto > hmm0/hmmdefs

# Train models with EM
HERest -C ../config/config -I ../etc/phones.train -t 250.0 150.0 1000.0 -S train.scp -H hmm0/macros -H hmm0/hmmdefs \
		-M hmm1 ../etc/monophones+sil

HERest -C ../config/config -I ../etc/phones.train -t 250.0 150.0 1000.0 -S train.scp -H hmm1/macros -H hmm1/hmmdefs \
		-M hmm2 ../etc/monophones+sil

# Copy model from hmm2 to hmm3
# Add sp state referecing intermidiate silence state
# create etc/sil.hed file for HHEd command (in book)
HHEd -H hmm3/macros -H hmm3/hmmdefs -M hmm4 ../etc/sil.hed ../etc/monophones+sil

# Create phones with 'sp' between words
HLEd -l '*' -d dictl40 -i phones1.train mkphones.led mlfwords.train

# Train model with 'sp' phono
HERest -C ../config/config -I ../etc/phones1.train -t 250.0 150.0 1000.0 -S train.scp -H hmm4/macros -H hmm4/hmmdefs \
		-M hmm5 ../etc/monophones+sil

# Create vocabulary
cat promptsl40.test | awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > vocab
# Create train.txt
cat promptsl40.test | awk '{for(i=2;i<=NF;i++){printf "%s ", $i} printf "/n"}' > train.txt
# Create languge model
/usr/local/speechapp/srilm/bin/i686-m64/ngram-count -order 2 -text train.txt -lm lml40  -ukndiscount2  -vocab vocab

# Create 'wordnet' for HTK format
HBuild -n lml40 -s '<s>' '</s>' vocab wordnet

# Do the Viterbi alg
ls ../datos/mfc/test/*/*.mfc > test.scp
HVite -C ../config/config -H ../modelos/hmm6/macros -H ../modelos/hmm6/hmmdefs -S test.scp
	-l '*' -i recout.mlf -w ../lm/wordnet -p 0.0 -s 5.0 ../etc/dictl40 ../etc/monophones+sil

#####################################
### Change how many gaussians are ###
#####################################

HHEd -H hmm6/macros -H hmm6/hmmdefs -M hmm7 ../rec/editf2g ../etc/monophones+sil
HERest -C ../config/config -I ../etc/phones1.train -t 250.0 150.0 1000.0 -S train.scp -H hmm7/macros -H hmm7/hmmdefs -M hmm8 ../etc/monophones+sil

# Show and count results
HResults -f -t -I ../etc/mlfwords.test ../lm/vocab recout-1.mlf





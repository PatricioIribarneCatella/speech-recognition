# NOTAS HTK

Procesamiento del Habla (66.43) - FIUBA


## Generación del los coeficientes _MFCC_

```bash
HCopy -A -V -T 1 -C config.hcopy -S genmfc.train 
HCopy -A -V -T 1 -C config.hcopy -S genmfc.test 
```

Utilizando el comando `HCopy` se realiza una traducción de los archivos _WAV_ a los coeficientes _MFCC: Mell Frequency Cepstrum Coefficients_. En los archivos _genmfc.train_ y _genmfc.test_ se especifica cómo debe realizarse ese mapeo, es decir, se indica cuál archivo _WAV_ corresponde con cuál archivo _MFCC_. Por otro lado, en el archivo _config.hcopy_ se declaran los atributos que deben tener los coeficientes _MFCC_ a generar. Por ejemplo, cuál va a ser el tamaño de ventana a utilizar, cuál va a ser la tasa de muestreo de dichas ventanas, el tipo de ventana a aplicar, y cuántos coeficientes dejar luego de la etapa de _liftering_, entre otros.

```
 # Coding parameters
 TARGETKIND = MFCC_0
 TARGETRATE = 100000.0
 SAVECOMPRESSED = T
 SAVEWITHCRC = T
 WINDOWSIZE = 250000.0
 USEHAMMING = T
 PREEMCOEF = 0.97
 NUMCHANS = 26
 CEPLIFTER = 22
 NUMCEPS = 12
 ENORMALISE = F
 SOURCEFORMAT = NIST
```

## Generación de la _word-list_ mediante el uso de _prompts_

```bash
cat promptsl40.train promptsl40.test |\
	 awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > wlistl40
```

Los archivos _promptsl40.train_ y _promptsl40.test_ contienen las transcripciones de todas las frases dichas en las grabaciones de la base de datos _latino40_. Para poder utilizar el _HTK_ se debe confeccionar un archivo que contenga todas las palabras dichas en cada una de las frases, para luego poder convertirlas en los sonidos fonéticos de cada una. 

## Creación del diccionario fonético

Si bien ya se dispone de todas las frases transcriptas y de todas las palabras que en ellas aparecen, todavía no se tiene la pronunciación fonética de las mismas. Justamente ésto es lo que se necesita a la hora de poder entrenar, y reconecer posteriormente, frases nuevas. Para ello se utiliza el comando `HDMan` el cual toma como _inputs_ a la lista de palabras generadas anteriormente, una lista de todos los modelos fonéticos de nuestro idioma, y un diccionario completo de todas las palabras posibles junto con su descomposición en fonemas. Finalmente devuelve como _output_, un diccionario de las palabras utilizadas con su descomposición fonética.

```bash
HDMan -m -w wlistl40 -g global.ded -n monophones+sil dictl40 lexicon
```

## Transformación de los datos en lenguaje _HTK_

En este momento se dispone de los siguientes datos: por un lado se tienen las transcripciones de las frases dichas en las grabaciones, y por otro se posee una descomposición fonética de cada una de las palabras que figuran en dichas frases. Lo que se necesita ahora, es transformar estos datos para que el _HTK_ pueda interpretarlos adecuadamente. _HTK_ funciona con lo que se denominan _MLF (Master Label File)_. Éstos no son nada más ni nada menos que los mismos datos que están en los archivos _promptsl40_ pero con un formato particular para _HTK_. Se utiliza un _script_ proporcionado por la cátedra para convertirlos de la siguiente manera:

```bash
prompts2mlf mlfwords.test promptsl40.test
prompts2mlf mlfwords.train promptsl40.train
```

Por último es necesario también, convertir el el _MLF_ de palabras, mediante el uso del diccionario creado en el paso anterior, a un _MLF_ de fonemas. Ésto se hace utilizando el comando `HLed` que es el _editor_ de _MLF_, de la siguiente forma:

```bash
HLEd -l '*' -d dictl40 -i mlfphones.train mkphones-sp.led mlfwords.train
```

# Generate intial parameters: {means, vars, transmat}
# (Previously create dirs: {hmm0, hmm1,...,hmm5})
```bash
cd modelos
ls ../datos/mfc/train/*/*.mfc > train.scp
HCompV -C ../config/config -f 0.01 -m -S train.scp -M hmm0 hmm0/proto
```

# Create 'macros' and 'hmmdefs' for proto
```bash
../scripts/go.gen-macros hmm0/vFloors hmm0/proto > hmm0/macros
../scripts/go.gen-hmmdefs ../etc/monophones+sil hmm0/proto > hmm0/hmmdefs
```

# Train models with EM
```bash
HERest -C ../config/config -I ../etc/phones.train -t 250.0 150.0 1000.0 -S train.scp -H hmm0/macros -H hmm0/hmmdefs \
		-M hmm1 ../etc/monophones+sil

HERest -C ../config/config -I ../etc/phones.train -t 250.0 150.0 1000.0 -S train.scp -H hmm1/macros -H hmm1/hmmdefs \
		-M hmm2 ../etc/monophones+sil
```

# Copy model from hmm2 to hmm3
# Add sp state referecing intermidiate silence state
# create etc/sil.hed file for HHEd command (in book)
```bash
HHEd -H hmm3/macros -H hmm3/hmmdefs -M hmm4 ../etc/sil.hed ../etc/monophones+sil
```

# Create phones with 'sp' between words
```bash
HLEd -l '*' -d dictl40 -i phones1.train mkphones.led mlfwords.train
```

# Train model with 'sp' phono
```bash
HERest -C ../config/config -I ../etc/phones1.train -t 250.0 150.0 1000.0 -S train.scp -H hmm4/macros -H hmm4/hmmdefs \
		-M hmm5 ../etc/monophones+sil
```

# Create vocabulary
```bash
cat promptsl40.test | awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > vocab
```
# Create train.txt
```bash
cat promptsl40.test | awk '{for(i=2;i<=NF;i++){printf "%s ", $i} printf "/n"}' > train.txt
```
# Create languge model
```bash
/usr/local/speechapp/srilm/bin/i686-m64/ngram-count -order 2 -text train.txt -lm lml40  -ukndiscount2  -vocab vocab
```

# Create 'wordnet' for HTK format
```bash
HBuild -n lml40 -s '<s>' '</s>' vocab wordnet
```

# Do the Viterbi alg
```bash
ls ../datos/mfc/test/*/*.mfc > test.scp
HVite -C ../config/config -H ../modelos/hmm6/macros -H ../modelos/hmm6/hmmdefs -S test.scp
	-l '*' -i recout.mlf -w ../lm/wordnet -p 0.0 -s 5.0 ../etc/dictl40 ../etc/monophones+sil
```

#####################################
### Change how many gaussians are ###
#####################################

```bash
HHEd -H hmm6/macros -H hmm6/hmmdefs -M hmm7 ../rec/editf2g ../etc/monophones+sil
HERest -C ../config/config -I ../etc/phones1.train -t 250.0 150.0 1000.0 -S train.scp -H hmm7/macros -H hmm7/hmmdefs -M hmm8 ../etc/monophones+sil
```

# Show and count results
```bash
HResults -f -t -I ../etc/mlfwords.test ../lm/vocab recout-1.mlf
```





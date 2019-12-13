# NOTAS HTK

Procesamiento del Habla (66.43) - FIUBA


## Generación del los coeficientes _MFCC_

```bash
$ HCopy -A -V -T 1 -C config.hcopy -S genmfc.train 
$ HCopy -A -V -T 1 -C config.hcopy -S genmfc.test 
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
$ cat promptsl40.train promptsl40.test |\
	 awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > wlistl40
```

Los archivos _promptsl40.train_ y _promptsl40.test_ contienen las transcripciones de todas las frases dichas en las grabaciones de la base de datos _latino40_. Para poder utilizar el _HTK_ se debe confeccionar un archivo que contenga todas las palabras dichas en cada una de las frases, para luego poder convertirlas en los sonidos fonéticos de cada una. 


## Creación del diccionario fonético

Si bien ya se dispone de todas las frases transcriptas y de todas las palabras que en ellas aparecen, todavía no se tiene la pronunciación fonética de las mismas. Justamente ésto es lo que se necesita a la hora de poder entrenar, y reconecer posteriormente, frases nuevas. Para ello se utiliza el comando `HDMan` el cual toma como _inputs_ a la lista de palabras generadas anteriormente, una lista de todos los modelos fonéticos de nuestro idioma, y un diccionario completo de todas las palabras posibles junto con su descomposición en fonemas. Finalmente devuelve como _output_, un diccionario de las palabras utilizadas con su descomposición fonética.

```bash
$ HDMan -m -w wlistl40 -g global.ded -n monophones+sil dictl40 lexicon
```


## Transformación de los datos en lenguaje _HTK_

En este momento se dispone de los siguientes datos: por un lado se tienen las transcripciones de las frases dichas en las grabaciones, y por otro se posee una descomposición fonética de cada una de las palabras que figuran en dichas frases. Lo que se necesita ahora, es transformar estos datos para que _HTK_ pueda interpretarlos adecuadamente. _HTK_ funciona con lo que se denominan _MLF (Master Label File)_. Éstos no son nada más ni nada menos que los mismos datos que están en los archivos _promptsl40_ pero con un formato particular para _HTK_. Se utiliza un _script_ proporcionado por la cátedra para convertirlos, de la siguiente manera:

```bash
$ prompts2mlf mlfwords.test promptsl40.test
$ prompts2mlf mlfwords.train promptsl40.train
```

Por último es necesario también, convertir el _MLF_ de palabras, mediante el uso del diccionario creado en el paso anterior, a un _MLF_ de fonemas. Ésto se hace utilizando el comando `HLed` que es el _editor_ de _MLF_, de la siguiente forma:

```bash
$ HLEd -l '*' -d dictl40 -i mlfphones.train mkphones-sp.led mlfwords.train
```

Como se puede ver, se utilizan como _inputs_ el diccionario (_dictl40_), el _MLF_ de palabras, y un archivo de configuración _mkphones-sp.led_, el cual contiene instrucciones necesarias para poder parsear las palabras contenidas en _mlfwords.train_ y transformalas en fonemas.


## Entrenamiento

Para poder ejecutar el algoritmo de _Baum-Welch_, primero se necesita realizar una inicialización adecuada de los parámetros como ser, la media, la varianza y la matriz de transición de todos los estados de cada una de las palabras, para cada una de las frases. Para ello, se utiliza el comando `HCompV` que genera valores iniciales en un archivo de _output_ llamado _proto_.

### Inicialización

```bash
$ ls ../datos/mfc/train/*/*.mfc > train.scp
$ HCompV -C ../config/config -f 0.01 -m -S train.scp -M hmm0 hmm0/proto
```

Por último, es necesario crear los archivos que _HTK_ emplea para realizar el algoritmo _BW_ que son: _macros_ y _hmmdefs_. Para conseguirlos se utilizan dos _scripts_ provistos por la cátedra que transforman los datos en _proto_ y generan los primeros datos para poder ejecutar la primera corrida de _BW_.

```bash
$ ./go.gen-macros hmm0/vFloors hmm0/proto > hmm0/macros
$ ./go.gen-hmmdefs monophones+sil hmm0/proto > hmm0/hmmdefs
```

Una inspección a las primeras líneas del archivo _proto_ muestra lo siguiente:

```
~o
<STREAMINFO> 1 39
<VECSIZE> 39<NULLD><MFCC_D_A_0><DIAGC>
~h "proto"
<BEGINHMM>
<NUMSTATES> 5
<STATE> 2
<MEAN> 39
 -7.610806e+00 -4.806953e+00 3.343384e+00 -4.409364e+00 -3.260492e+00
 -1.204213e+00 -1.027766e+00 1.860029e-01 -4.707533e-01 4.288140e-01
  2.212882e-01 6.037196e-01 6.124635e+01 -3.317322e-04 3.268267e-04
 -4.727239e-04 -1.007655e-04 5.489814e-04 4.647013e-04 -2.713677e-04
 -2.866100e-05 -7.021228e-04 8.786149e-04 -6.662139e-05 -5.925029e-04
  3.041824e-04 1.543509e-05 2.458352e-05 5.736159e-05 1.143577e-04
 -1.902081e-05 -2.473935e-05 -6.246736e-05 -1.556318e-04 -6.903148e-05
 -3.499124e-05 6.290742e-06 3.600528e-05 -6.744299e-05
<VARIANCE> 39
 4.912927e+01 3.201925e+01 4.591970e+01 6.982524e+01 7.528906e+01
 6.552078e+01 6.032398e+01 4.897406e+01 4.815772e+01 3.927904e+01
 4.544141e+01 3.637407e+01 1.020039e+02 2.270554e+00 1.836995e+00
 2.205474e+00 3.440568e+00 3.509371e+00 3.123952e+00 3.142145e+00
 3.095316e+00 2.873873e+00 2.637191e+00 2.526928e+00 2.136164e+00
 2.365552e+00 3.281180e-01 2.994132e-01 3.485773e-01 5.573778e-01
 5.800697e-01 5.454681e-01 5.530963e-01 5.582977e-01 5.185300e-01
 4.903159e-01 4.589276e-01 3.917152e-01 3.384365e-01
<GCONST> 1.254290e+02
```

Acá se aprecian los parámetros para el primer estado (el número dos simboliza el primer estado dentro de los tres que conforman cada una de los modelos para cada uno de los fonemas disponibles, ya que el número uno está destinado al estado inicial). Para ver cómo funciona el _script_ `go.gen-hmmdefs`. se muestra a continuación una inspección de las primeras líneas del archivo _hmmdefs_.

```
~h "aa"
<BEGINHMM>
<NUMSTATES> 5
<STATE> 2
<MEAN> 39
 -7.610806e+00 -4.806953e+00 3.343384e+00 -4.409364e+00 -3.260492e+00
 -1.204213e+00 -1.027766e+00 1.860029e-01 -4.707533e-01 4.288140e-01
  2.212882e-01 6.037196e-01 6.124635e+01 -3.317322e-04 3.268267e-04
 -4.727239e-04 -1.007655e-04 5.489814e-04 4.647013e-04 -2.713677e-04
 -2.866100e-05 -7.021228e-04 8.786149e-04 -6.662139e-05 -5.925029e-04
  3.041824e-04 1.543509e-05 2.458352e-05 5.736159e-05 1.143577e-04
 -1.902081e-05 -2.473935e-05 -6.246736e-05 -1.556318e-04 -6.903148e-05
 -3.499124e-05 6.290742e-06 3.600528e-05 -6.744299e-05
<VARIANCE> 39
 4.912927e+01 3.201925e+01 4.591970e+01 6.982524e+01 7.528906e+01
 6.552078e+01 6.032398e+01 4.897406e+01 4.815772e+01 3.927904e+01
 4.544141e+01 3.637407e+01 1.020039e+02 2.270554e+00 1.836995e+00
 2.205474e+00 3.440568e+00 3.509371e+00 3.123952e+00 3.142145e+00
 3.095316e+00 2.873873e+00 2.637191e+00 2.526928e+00 2.136164e+00
 2.365552e+00 3.281180e-01 2.994132e-01 3.485773e-01 5.573778e-01
 5.800697e-01 5.454681e-01 5.530963e-01 5.582977e-01 5.185300e-01
 4.903159e-01 4.589276e-01 3.917152e-01 3.384365e-01
<GCONST> 1.254290e+02

....

~h "bb"
<BEGINHMM>
<NUMSTATES> 5
<STATE> 2
<MEAN> 39
 -7.610806e+00 -4.806953e+00 3.343384e+00 -4.409364e+00 -3.260492e+00
 -1.204213e+00 -1.027766e+00 1.860029e-01 -4.707533e-01 4.288140e-01
  2.212882e-01 6.037196e-01 6.124635e+01 -3.317322e-04 3.268267e-04
 -4.727239e-04 -1.007655e-04 5.489814e-04 4.647013e-04 -2.713677e-04
 -2.866100e-05 -7.021228e-04 8.786149e-04 -6.662139e-05 -5.925029e-04
  3.041824e-04 1.543509e-05 2.458352e-05 5.736159e-05 1.143577e-04
 -1.902081e-05 -2.473935e-05 -6.246736e-05 -1.556318e-04 -6.903148e-05
 -3.499124e-05 6.290742e-06 3.600528e-05 -6.744299e-05
<VARIANCE> 39
 4.912927e+01 3.201925e+01 4.591970e+01 6.982524e+01 7.528906e+01
 6.552078e+01 6.032398e+01 4.897406e+01 4.815772e+01 3.927904e+01
 4.544141e+01 3.637407e+01 1.020039e+02 2.270554e+00 1.836995e+00
 2.205474e+00 3.440568e+00 3.509371e+00 3.123952e+00 3.142145e+00
 3.095316e+00 2.873873e+00 2.637191e+00 2.526928e+00 2.136164e+00
 2.365552e+00 3.281180e-01 2.994132e-01 3.485773e-01 5.573778e-01
 5.800697e-01 5.454681e-01 5.530963e-01 5.582977e-01 5.185300e-01
 4.903159e-01 4.589276e-01 3.917152e-01 3.384365e-01
<GCONST> 1.254290e+02

....
```

De esta forma, se puede ver, cómo ese estado _inicial_ que reside en _proto_ se copia para todos los fonemas disponibles en el archivo _monophones+sil_.

### _Baum-Welch_

Se ejecuta el algoritmo _Baum-Welch_ mediante el comando `HERest`. Como se puede ver, se toma como modelo incial el que se generó anteriormente en hmm0, y la _re-estimación_ que genera _HTK_ se guarda en hmm1. Para poder construir mejores modelos, se realiza una segunda _re-estimación_ que se guarda en hmm2.

```bash
$ HERest -C config -I phones.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm0/macros -H hmm0/hmmdefs -M hmm1 monophones+sil

$ HERest -C config -I phones.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm1/macros -H hmm1/hmmdefs -M hmm2 monophones+sil
```

Cabe destacar, que el comando `HERest` no solo ejecuta el algoritmo de _Baum-Welch_ sino que también construye como primera etapa, todos los modelos de cada uno de los fonemas disponibles en el archivo _monophones+sil_ y luego sobre éstos es que ejecuta dicho algoritmo.

### Agregado del fonema _sp: short pause_

Hasta ahora la concatenación de palabras (que a su vez es una concatenación de fonemas) dentro de una frase, se hace tomando el estado final de una palabra y uniéndolo con el estado inicial de la siguiente, si lugar para que el hablante haga algún tipo de pausa entre medio. Esto funciona bien, salvo para los casos en los que hablante sí realiza una pausa corta entre palabras. Para que el modelo sea versátil y que permita ambas situaciones, es que se decide incluir un nuevo fonema llamado _sp: short pause_. Éste se modela de una forma distinta a cómo se hacen los demás modelos fonéticos, y se realiza de la siguiente forma:

![Modelo de Markov para los fonemas](phones-model.png)


![Modelo de Markov para el estado _sp_](sp-model.png)

Los parámetros que se utilizan en este único estado son los mismos que tiene el estado intermedio del modelo de tres estados del fonema _sil_. Para conseguir ésto, se copian los parámetros del modelo 2 (entrenado sin el fonema _sp_) al modelo 3 (teniendo en cuenta que este nuevo fonema contine únicamente un estado y que cuya matriz de transición es de 3x3 y no de 5x5 como las demás), se agrega el nuevo fonema al archvivo _monophones+sil+sp_, y se editan los archivos que conforman el modelo con un nuevo comando llamado `HHEd` (editor de modelos _hmm_). A éste se le pasa un archivo de configuración _sil.hed_, el cual contiene instrucciones de cómo modificar la matriz de transición de este nuevo fonema para contemplar las transiciones que se ven en la Fig.2.

```bash
$ HHEd -H hmm3/macros -H hmm3/hmmdefs -M hmm4 sil.hed monophones+sil+sp
```

El archivo de configuración _sil.hed_ contiene lo siguiente:

```
 AT 2 4 0.2 {sil.transP}
 AT 4 2 0.2 {sil.transP}
 AT 1 3 0.3 {sp.transP}
 TI silst {sil.state[3], sp.state[2]}
```



# Copy model from hmm2 to hmm3
# Add sp state referecing intermidiate silence state
# create etc/sil.hed file for HHEd command (in book)


# Create phones with 'sp' between words
```bash
HLEd -l '*' -d dictl40 -i phones1.train mkphones.led mlfwords.train
```

# Train model with 'sp' phono

```bash
HERest -C ../config/config -I ../etc/phones1.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm4/macros -H hmm4/hmmdefs -M hmm5 ../etc/monophones+sil

HERest -C ../config/config -I ../etc/phones1.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm5/macros -H hmm5/hmmdefs -M hmm6 ../etc/monophones+sil
```







## Reconocimiento

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





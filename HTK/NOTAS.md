---
title: "Notas HTK"
author:
- Patricio Iribarne Catella
- Procesamiento del Habla (66.43) - FIUBA
date:
- 13 de Diciembre, 2019
theme:
- Copenhagen
---

## Generación del los coeficientes _MFCC_

```bash
$ HCopy -A -V -T 1 -C config.hcopy -S genmfc.train 
$ HCopy -A -V -T 1 -C config.hcopy -S genmfc.test 
```

Utilizando el comando `HCopy` se realiza una traducción de los archivos _WAV_ a los coeficientes _MFCC: Mell Frequency Cepstrum Coefficients_. En los archivos _genmfc.train_ y _genmfc.test_ se especifica cómo debe realizarse ese mapeo, es decir, se indica cuál archivo _WAV_ corresponde con cuál archivo _MFCC_. Por otro lado, en el archivo _config.hcopy_ se declaran los atributos que deben tener los coeficientes _MFCC_ a generar. Por ejemplo, cuál va a ser el tamaño de ventana a utilizar, cuál va a ser la tasa de muestreo de dichas ventanas, el tipo de ventana a aplicar, cuántos coeficientes dejar luego de la etapa de _liftering_ y el formato de los archivos de audio (_NIST_ en este caso), entre otros.

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

Si bien ya se dispone de todas las frases transcriptas y de todas las palabras que en ellas aparecen, todavía no se tiene la pronunciación fonética de las mismas. Justamente ésto es lo que se necesita a la hora de poder entrenar, y reconocer posteriormente, frases nuevas. Para ello se utiliza el comando `HDMan` el cual toma como _inputs_ a la lista de palabras generadas anteriormente (_wlistl40_), y un diccionario completo de todas las palabras posibles junto con su descomposición en fonemas (_lexicon_). Finalmente devuelve como _outputs_, un diccionario de las palabras utilizadas con su descomposición fonética, y una lista de todos los fonemas encontrados durante su creación. Ésta es la lista de modelos fonéticos a generar.

```bash
$ HDMan -m -w wlistl40 -g global.ded -n monophones+sil dictl40 lexicon
```

Un archivo interesante de explicar en este punto es _global.ded_, que es un archivo de edición del diccionario. Se utiliza el comando `AS sp` para agregar al final de cada una de las frases un fonema denominado _sp_. Luego se explicará el significado de este fonema y cuál es su utilidad, ya que ahora no se utilizará por tener una topología diferente del resto de los fonemas (todos poseen tres estados, éste posee sólo uno).

Otro fonema que se agrega (al archivo _monophones+sil_) al finalizar la ejecución del comando `HDMan` es _sil_, que simboliza un _silencio_ con topología de tres estados como todos los otros fonemas. Éste se utiliza al comienzo y final de cada frase como se verá a continuación.

## Transcripciones (_labels_) en lenguaje _HTK_

En este momento se dispone de los siguientes datos: por un lado se tienen las transcripciones de las frases dichas en las grabaciones, y por otro se posee una descomposición fonética de cada una de las palabras que figuran en dichas frases. Lo que se necesita ahora, es transformar estos datos para que _HTK_ pueda interpretarlos adecuadamente. _HTK_ funciona con lo que se denominan _MLF (Master Label File)_. Éstos no son nada más ni nada menos que los mismos datos que están en los archivos _promptsl40_ pero con un formato particular para _HTK_. Se utiliza un _script_ proporcionado por la cátedra para convertirlos en _label-files_ a nivel palabra, de la siguiente manera:

```bash
$ prompts2mlf mlfwords.test promptsl40.test
$ prompts2mlf mlfwords.train promptsl40.train
```

Por último es necesario también, convertir el _MLF_ de palabras, mediante el uso del diccionario creado en el paso anterior, a un _MLF_ de fonemas. Ésto se hace utilizando el comando `HLed` que es el _editor_ de _MLF_, de la siguiente forma:

```bash
$ HLEd -l '*' -d dictl40 -i mlfphones.train mkphones-sp.led mlfwords.train
```

Como se puede ver, se utilizan como _inputs_ el diccionario (_dictl40_), el _MLF_ de palabras, y un archivo de configuración _mkphones-sp.led_, el cual contiene instrucciones necesarias para poder parsear las palabras contenidas en _mlfwords.train_ y transformarlas en fonemas. Dichas instrucciones son:

```
 EX
 IS sil sil
 DE sp
```

De esta forma, el comando `EX` expande cada una de las palabras contenidas en cada una de las frases del _MLF_ e inserta sus respectivos fonemas (de acuerdo a lo que dice el diccionario), el comando `IS` inserta un fonema _sil_ al comienzo y al final de la frase, y el comando `DE` borra el fonema _sp_ agregado anteriormente, ya que en esta etapa no se desea entrenar el modelo conteniendo dicho fonema.


## Entrenamiento

Para poder ejecutar el algoritmo de _Baum-Welch_, primero se necesita realizar una inicialización adecuada de los parámetros como ser, la media, la varianza y la matriz de transición de todos los estados de cada una de las palabras, para cada una de las frases. Para ello, se utiliza el comando `HCompV` que genera valores iniciales en un archivo de _output_ llamado _proto_.

### Inicialización

```bash
$ ls datos/mfc/train/*/*.mfc > train.scp
$ HCompV -C config -f 0.01 -m -S train.scp -M hmm0 hmm0/proto
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

Se ejecuta el algoritmo _Baum-Welch_ mediante el comando `HERest`. Como se puede ver, se toma como modelo inicial el que se generó anteriormente en _hmm0_, y la _re-estimación_ que genera _HTK_ se guarda en _hmm1_. Para poder construir mejores modelos, se realiza una segunda _re-estimación_ que se guarda en _hmm2_.

```bash
$ HERest -C config -I mlfphones.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm0/macros -H hmm0/hmmdefs -M hmm1 monophones+sil

$ HERest -C config -I mlfphones.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm1/macros -H hmm1/hmmdefs -M hmm2 monophones+sil
```

Cabe destacar, que el comando `HERest` no solo ejecuta el algoritmo de _Baum-Welch_ sino que también construye como primera etapa, todos los modelos de cada uno de los fonemas disponibles en el archivo _monophones+sil_ y utilizando los _MLF_ anteriores construye la cadena de estados de cada frase. Finalmente sobre éstos es que ejecuta dicho algoritmo.

### Agregado del fonema _sp: short pause_

Hasta ahora la concatenación de palabras (que a su vez es una concatenación de fonemas) dentro de una frase, se hace tomando el estado final de una palabra y uniéndolo con el estado inicial de la siguiente, sin lugar para que el hablante haga algún tipo de pausa entre medio. Esto funciona bien, salvo para los casos en los que el hablante sí realiza una pausa corta entre palabras. Para que el modelo sea versátil y que permita ambas situaciones, es que se decide incluir un nuevo fonema llamado _sp: short pause_. Éste se modela de una forma distinta a cómo se hacen los demás modelos fonéticos, y se realiza de la siguiente forma:

![Modelo de Markov para los fonemas](phones-model.png)


![Modelo de Markov para el fonema _sp_](sp-model.png)

Los parámetros que se utilizan en este único estado son los mismos que tiene el estado intermedio del modelo de tres estados del fonema _sil_. Para conseguir ésto, se copian los parámetros del modelo 2 (entrenado sin el fonema _sp_) al modelo 3 (teniendo en cuenta que este nuevo fonema contiene únicamente un estado y cuya matriz de transición es de 3x3 y no de 5x5 como las demás), se agrega el nuevo fonema al archivo _monophones+sil+sp_, y se editan los archivos que conforman el modelo con un nuevo comando llamado `HHEd` (editor de modelos _hmm_). A éste se le pasa un archivo de configuración _sil.hed_, el cual contiene instrucciones de cómo modificar la matriz de transición de este nuevo fonema para contemplar las transiciones que se ven en la figura 2 (Figure.2).

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

El comando _AT (add transition)_ agrega nuevas transiciones entre dos estados, y el comando _TI (tied-state)_ crea un _link_ para compartir dos estados. En este caso, se agregan transiciones para la matriz de transición del fonema _sil_ para unir los estados extremos 2 y 4 entre sí, y una nueva transición entre los estados inicial y final del fonema _sp_ 1 y 3. Esto último se hace para considerar los dos casos en que haya o no, una pausa entre palabras. Finalmente se crea un _link_ entre el estado intermedio del fonema _sil_ y el estado del fonema _sp_, para que se utilicen los mismos parámetros en las gaussianas utilizadas en dichos estados.


Por último, se debe modificar el _MLF_ de fonemas que se posee actualmente para incluir el nuevo fonema _sp_. Para ello, se vuelve a utilizar el comando `HLEd`. En este caso el archivo _mkphones.led_ es ligeramente modificado para que no remueva los fonemas _sp_ como sí se había hecho anteriormente.

```bash
$ HLEd -l '*' -d dictl40 -i mlfphones1.train mkphones.led mlfwords.train
```

Finalmente, se re-entrenan los modelos con dos pasadas como se hizo con los modelos previos.

```bash
$ HERest -C config -I mlfphones1.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm4/macros -H hmm4/hmmdefs -M hmm5 monophones+sil+sp

$ HERest -C config -I mlfphones1.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm5/macros -H hmm5/hmmdefs -M hmm6 monophones+sil+sp
```

### Modificación de la cantidad de _Gaussianas_

Para poder mejor los modelos utilizados en el _reconocimiento_ y que la precisión sea cada vez mejor, los modelos se modifican para permitir que la cantidad de _Gaussianas_ en cada estado sea mayor que uno. De esta forma lo que se tiene es una mezcla de _Gaussianas_ es cada estado. En este se vuelve a utilizar el comando `HHEd`, para modificar los _hmmdefs_ y _macros_ del último modelo (en este caso el número 6). El archivo _editf2g_ contiene instrucciones para modificar las medias y las varianzas de cada gaussiana actual y generar nuevas medias y varianzas iniciales que serán re-entrenadas con _Baum-Welch_.

```bash
$ mv hmm6 hmm-1-3

$ HHEd -H hmm-1-3/macros -H hmm-1-3/hmmdefs -M hmm-2-1 editf2g monophones+sil+sp
```

Por último, se vuelve a re-entrenar el modelo con dos pasadas del algoritmo _Baum-Welch_.

```bash
$ HERest -C config -I mlfphones1.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm-2-1/macros -H hmm-2-1/hmmdefs -M hmm-2-2 monophones+sil+sp

$ HERest -C config -I mlfphones1.train -t 250.0 150.0 1000.0 -S train.scp \
	-H hmm-2-2/macros -H hmm-2-2/hmmdefs -M hmm-2-3 monophones+sil+sp
```

Finalmente, ésto se realiza para distinta cantidad de _Gaussianas_, que en este caso van a ser las siguientes: _2, 4, 8, 16, 32, 64, 128, 256_ con lo cual se van a tener 9 modelos a los cuales se les va a aplicar el _reconocimiento_ utilizando el algoritmo de _Viterbi_.



## Reconocimiento

Como se mencionó en el punto anterior, se va aplicar el algoritmo de _Viterbi_ para poder reconocer las palabras que se encuentran en el _set_ de _test_. Pero primero, hay que crear varios archivos que componen los _inputs_ de un nuevo comando de _HTK_ denominado _HVite_.

### Modelo de lenguaje: qué es y para qué sirve

- Vocabulario

Este archivo contiene todas las palabras utilizadas en el _set_ de _test_ de la base de datos. Equivalente al archivo _wlistl40_ generado anteriormente.

```bash
$ cat promptsl40.test | \
	awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > vocab
```

- Lista de frases

Contiene todas las frases que se usaron para entrenar a los modelos y que ahora se utilizan para poder generar un modelo lingüístico.

```bash
$ cat promptsl40.train | \
	awk '{for(i=2;i<=NF;i++){printf "%s ", $i} printf "/n"}' > train.txt
```

- Modelo lingüístico

Utilizando otra aplicación, se construye el modelo lingüístico estadístico. Éste se calcula teniendo en cuenta la generación de _bigramas_ como contexto de cada palabra.

```bash
$ /usr/local/speechapp/srilm/bin/i686-m64/ngram-count -order 2 \
	-text train.txt -lm lml40 -ukndiscount2 -vocab vocab
```

- Red de palabras (en formato _HTK_)

Simplemente traduce el modelo lingüístico anterior a una red de palabras que es interpretada por _HTK_. Se le indica al _HTK_ cuáles son los _labels_ de comienzo (_start_) y de final (_end_) mediante el parámetro `-s` ya que dichas _labels_ se agregaron tanto a la lista de palabras como al diccionario.

```bash
$ HBuild -n lml40 -s '<s>' '</s>' vocab wordnet
```

### _Viterbi_

Se utiliza el comando `HVite` considerando como _inputs_ al diccionario, a la red de palabras, a todos los fonemas, y a los datos propiamente dichos que son los _MFCC_ de _test_. Genera como _output_ el archivo _recout-1.mlf_ que es un archivo _MLF_ de las frases reconocidas.

Cabe destacar, que este comando no sólo realiza el algoritmo de _Viterbi_ en sí, sino que también realiza una etapa de inicialización en la cual se construye toda la red estados posibles y por ende la correspondiente matriz de transición, teniendo en cuenta las probabilidades que se hallaron antes con el modelo lingüístico. Luego se ejecuta el algoritmo en cuestión, y finalmente se pasa a una etapa de decodificación en la cual se encuentra la secuencia de palabras de la secuencia de estados óptima de cada frase.

```bash
$ ls datos/mfc/test/*/*.mfc > test.scp

$ HVite -C config -H hmm-1-3/macros -H hmm-1-3/hmmdefs -S test.scp \
	-l '*' -i recout-1.mlf -w wordnet -p 0.0 -s 5.0 \
	dictl40 monophones+sil+sp
```

## Resultados

Para mostrar los resultados estadísticos se procede a utilizar otro comando de _HTK_ denominado `HResults`, el cual toma como _inputs_ al _MLF_ de palabras del _set_ de _test_ (para poder corroborar a cuántas oraciones se identificó correctamente), el vocabulario (para poder saber a cuántas palabras se identificó correctamente), y el archivo que generó el comando anterior `HVite`.

```bash
$ HResults -f -t -I mlfwords.test vocab recout-1.mlf > recout-1.stats
```

Una inspección a este archivo nos muestra lo siguiente:

```
------------------------ Sentence Scores --------------------------
====================== HTK Results Analysis =======================
  Date: Wed Dec 11 17:31:42 2019
  Ref : ../etc/mlfwords.test
  Rec : recout-1.mlf
-------------------------- File Results ---------------------------
af14_001.rec:  100.00( 87.50)  [H=   8, D=  0, S=  0, I=  1, N=  8]
Aligned transcription: af14_001.lab vs af14_001.rec
 LAB:     no jugará el resto de la temporada regular 
 REC: qué no jugará el resto de la temporada regular 

....

------------------------ Overall Results --------------------------
SENT: %Correct=8.00 [H=79, S=908, N=987]
WORD: %Corr=59.58, Acc=46.54 [H=4713, D=395, S=2802, I=1032, N=7910]
===================================================================
```

Como se puede apreciar, la precisión en las oraciones es del 8% y para las palabras del casi 60%. Se lo puede comparar con el modelo de 256 gaussianas, el cual se muestra a continuación:

```
------------------------ Sentence Scores --------------------------
====================== HTK Results Analysis =======================
  Date: Wed Dec 11 17:32:48 2019
  Ref : ../etc/mlfwords.test
  Rec : recout-256.mlf
-------------------------- File Results ---------------------------
af14_001.rec:  100.00(100.00)  [H=   8, D=  0, S=  0, I=  0, N=  8]
af14_002.rec:   88.89( 88.89)  [H=   8, D=  0, S=  1, I=  0, N=  9]
Aligned transcription: af14_002.lab vs af14_002.rec
 LAB: me he repuesto más rápidamente de lo que pensaba 
 REC: no he repuesto más rápidamente de lo que pensaba 

....

------------------------ Overall Results --------------------------
SENT: %Correct=46.30 [H=457, S=530, N=987]
WORD: %Corr=85.16, Acc=80.61 [H=6736, D=174, S=1000, I=360, N=7910]
===================================================================
```

En este caso se ve cómo mejora la precisión, ya que para las oraciones se tiene un 46%, y para las palabras un 85%.

A continuación se muestran los resultados completos para cada una de las cantidades de gaussianas elegidas.

- 1 _Gaussiana_
	- Oraciones: 8%
	- Palabras: 59.58%
- 2 _Gaussianas_
	- Oraciones: 12.66%
	- Palabras: 65.17%
- 4 _Gaussianas_
	- Oraciones: 23.51%
	- Palabras: 72.45%
- 8 _Gaussianas_
	- Oraciones: 30.29%
	- Palabras: 77.35%
- 16 _Gaussianas_
	- Oraciones: 35.66%
	- Palabras: 80.57%
- 32 _Gaussianas_
	- Oraciones: 41.74%
	- Palabras: 83.17%
- 64 _Gaussianas_
	- Oraciones: 45.49%
	- Palabras: 84.72%
- 128 _Gaussianas_
	- Oraciones: 46.20%
	- Palabras: 85.46%
- 256 _Gaussianas_
	- Oraciones: 46.30%
	- Palabras: 85.16%

Como se puede apreciar, con 256 _Gaussianas_ los resultados son los mejores con lo cual se decide utilizar este modelo.


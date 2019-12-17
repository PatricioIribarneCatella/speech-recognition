---
title: "Notas Gramática Finita"
author:
- Patricio Iribarne Catella
- Procesamiento del Habla (66.43) - FIUBA
date:
- 16 de Diciembre, 2019
theme:
- Copenhagen
---


## Generación de las reglas gramaticales

Teniendo en cuenta el lenguaje para describir reglas de gramática, según figura en el ejemplo del _htkbook_, se generaron las siguientes reglas.

```
$digit = uno | dos | tres | cuatro | cinco |
	 	seis | siete | ocho | nueve | cero;

$name = juan [ fernandez ] |
		pedro [ rodriguez ] |
		andrea [ perez ] |
		juana |
		patricia |
		andres;

(enviar-com
	((llame | llamar) al <$digit> |
	((llame | llamar) a | comuniqueme con) $name)
enviar-fin)
```

De acuerdo con ésto, existen dos variables llamadas `digit` y `name` cuyos valores se pueden combinar arbitrariamente respetando la regla de conformación de frases. Luego por ejemplo, es una frase válida _envia-com llame al 5468_ enviar-fin, o _envia-com comuniqueme con pedro rodriguez_, pero no es una oración permitida _envia-com llame a 7859 enviar-fin_, o _envia-com llamar al andres enviar-fin_. Esta gramática se guarda en el archivo _grammar_ utilizado en el siguiente paso.


## Generación de la red de palabras

```bash
$ HParse grammar wordnet.gf
```

Se utiliza un nuevo comando llamado `HParse` que toma como _input_ la gramática creada en el paso anterior, y construye una red de palabras análoga a la red que se debía crear con el modelo de lenguaje estadísitico de bigramas. En este caso no es relevante que se disponga de un modelo estadísitico de bigramas ya que lo que se desea es que las transiciones sean equiprobables y que todas las frases tengan la misma opurtunidad de aparecer. Esta característica no es común a todas a las gramáticas finitas, ya que se podría requerir que dentro de la red de palabras reducidas algunas transiciones sean más probables que otras.


## Creación de un diccionario

En este caso el diccionario se crea de la misma forma que cuando se deseaba hacer un reconocedor de habla general, y eso es mediante el uso de un archivo _lexicon_ y un archivo _wlistgf_ (ambos proporcionados por la cátedra). En ellos figura, por un lado, una lista de todas las palabras posibles a utilizar junto con su descomposición en fonemas, y una lista de las palabras que realmente se van a utilizar, respectivamente. Se vuelve a utilizar el comando `HDMan` para crear este diccionario, junto con el archivo de _monophones+sil_ de los fonemas encontrados durante su creación.

```bash
$ HDMan -m -w wlistgf -g global.ded -n monophones+sil dictgf lexicongf
```

Se vuelve a utilizar el archivo _global.ded_, que es un archivo de edición del diccionario, y que contiene el comando `AS sp` para agregar al final de cada una de las palabras el fonema _sp_.


## El _libreto_

Lo que nos hace falta ahora es algo donde esté escrito qué es lo que debemos decir al micrófono para luego poder reconocerlo, y esto es lo que se denomina _el libreto_ (o _prompts_ en inglés). Se utilizará un nuevo comando `HSGen` que toma como _inputs_ al diccionario creado en el paso anterior, y a lista de palabras (_wordnet_), para crear una cantidad variada de frases teniendo en cuenta la gramática propuesta. En este caso se generarán 200 frases.

```bash
$ HSGen -l -n 200 wordnet.gf dictgf > promptsgf.test
```

Como analogía con el reconocedor de habla general, la base de datos de _latinos-40_ ya traía estos archivos para el _set_ de _train_ y el de _test_ para que luego nosotros podamos entrenarlo y reconocer las frases grabadas. Ahora nosotrosi, queremos grabar las frases a partir de este libreto.


## Grabación y conversión a coeficientes _MFCC_

Una vez grabadas todas las frases del _libreto_ en formato _WAV_ y a 16KHz como frecuencia de muestro, se deben convertir (o mejor dicho parametrizar) estas grabaciones a sus respectivos coeficientes _cepstrum_ o _MFCC_. Esto se logra, al igual que en el caso anterior, mediante el comando `HCopy` y utilizando el _script_ `go.genmfcgf` para crear un _mapping_ entre los archivos _.wav_ y los archivos _.mfc_. Es interesante destacar que para el archivo de configuración para `HCopy` fue necesario cambiar el atributo _SOURCEFORMAT_ a _WAV_ en vez del utilizado anteriormente _NIST_.

```bash
$ go.genmfcgf genmfc.gf

$ HCopy -A -V -T 1 -C gf.config.hcopy -S genmfc.gf 
```


## Reconocimiento

Nuevamente para el reconocimiento se utilizará el comando de _HTK_ llamado _HVite_. De igual forma que cuando se reconocía habla en general, es necesario que le pasemos a este comando, los modelos que se utilizaron en la etapa de entrenamiento, el diccionario, los fonemas utilizados y la red de palabras. Por último también hace falta un archivo que contenga los coeficientes _cepstrum_ de cada una de las grabaciones el cual se identifica como _testgf.scp_.

```bash
$ ls ../datos-gf/mfc/*.mfc > testgf.scp
```

```bash
$ HVite -C config -H hmm/macros -H hmm/hmmdefs -S testgf.scp \
	-l '*' -i recout-gf.mlf -w wordnet.gf -p 0.0 -s 5.0 \
	dictgf monophones+sil
```

Cabe destacar, que este comando no sólo realiza el algoritmo de _Viterbi_ en sí, sino que también realiza una etapa de inicialización en la cual se construye toda la red estados posibles y por ende la correspondiente matriz de transición, esta vez teniendo en cuenta que todas las transiciones son equiprobables. Luego se ejecuta el algoritmo en cuestión, y finalmente se pasa a una etapa de decodificación en la cual se encuentra la secuencia de palabras de la secuencia de estados óptima de cada frase.


## Resultados

Los resultados que se obtuvieron correponden utilizar los modelos entrenados con 64, 128 y 256 _Gaussianas_ generados a partir de el entrenamiento con la base de datos _latinos-40_. Pero para esto, primero hay que generar ciertos archivos que son necesarios, ellos son:

- Archivos en el formato _MLF_ del _HTK_

Se utiliza el _script_ proporcionado por la cátedra llamado `prompts2mlf`.

```bash
$ prompts2mlf mlfwordsgf.test promptsgf.test
```

- Vocabulario

Es necesario, al igual que lo fue en habla en general, tener un vocabulario con todas las palabras posibles de cada una de las frases sin repetir.

```bash
$ cat promptsgf.test | \
	awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > vocab.gf
```

Por último, se ejecuta el comando `HResults` de _HTK_, de la siguiente forma:

```bash
$ HResults -f -t -I mlfwordsgf.test vocab.gf recout-gf.mlf
```

A continuación se muestran los resultados obtenidos para cada una de las _Gaussianas_ elegidas anteriormente.

- 64 _Gaussianas_
	- Oraciones: 58.00%
	- Palabras: 94.68%
- 128 _Gaussianas_
	- Oraciones: 59.50%
	- Palabras: 93.17%
- 256 _Gaussianas_
	- Oraciones: 56.50%
	- Palabras: 90.62%

Como se puede apreciar, el mejor modelo para oraciones resulta ser el que utiliza 128 _Gaussianas_, pero el mejor para palabras es el que utiliza 64 _Gaussianas_.


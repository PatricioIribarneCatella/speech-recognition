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

## Generación de las reglas gramáticales

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


## Creación de un diccionario

from lexicongf and the wlistgf

```bash
$ HDMan -m -w wlistgf -g global.ded -n monophones+sil dictgf lexicongf
```


## El _libreto_

dictgf (all the words and their phonetics) and 
wordnet.gf (the word net with their connections) generate random phrases

```bash
$ HSGen -l -n 200 wordnet.gf dictgf > promptsgf.test
```


## Grabación y conversión a coeficientes _MFCC_

### Generate genmfc.gf mapping for HCopy input

```bash
$ go.genmfcgf genmfc.gf
```

```bash
$ HCopy -A -V -T 1 -C gf.config.hcopy -S genmfc.gf 
```


## Reconocimiento

```bash
$ ls ../datos-gf/mfc/*.mfc > testgf.scp
```

```bash
$ HVite -C config -H hmm-256-3/macros -H hmm-256-3/hmmdefs -S testgf.scp \
	-l '*' -i recout-gf.mlf -w wordnet.gf -p 0.0 -s 5.0 \
	dictgf monophones+sil
```


## Resultados

# Convert prompts into MLF-words
```bash
$ prompts2mlf mlfwordsgf.test promptsgf.test
```

# Create vocabulary
```bash
$ cat promptsgf.test | awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > vocab.gf
```

# Show and count results
```bash
$ HResults -f -t -I mlfwordsgf.test vocab.gf recout-gf.mlf
```


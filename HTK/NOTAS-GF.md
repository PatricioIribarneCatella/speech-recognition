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



grammar:

```
$digit = uno | dos | tres | cuatro | cinco | seis | siete | ocho | nueve | cero;
$name = juan [ fernandez ] | pedro [ rodriguez ] | andrea [ perez ] | juana | patricia | andres;
( enviar-com ( (llame | llamar) al <$digit> | ((llame | llamar) a | comuniqueme con) $name) enviar-fin )
```

# Generate 'word-net' with the grammar
HParse grammar wordnet.gf

# Generate the dictionary from the lexicongf and the wlistgf
HDMan -m -w wlistgf -g global.ded -n monophones+sil -l ../log/hdmangf.log dictgf lexicongf

# Considering dictgf (all the words and their phonetics) and 
# wordnet.gf (the word net with their connections) generate random phrases
HSGen -l -n 200 wordnet.gf dictgf > promptsgf.test

# Convert prompts into MLF-words
prompts2mlf mlfwordsgf.test promptsgf.test

# Create vocabulary
cat promptsgf.test | awk '{for(i=2;i<=NF;i++){print $i}}' | sort | uniq > vocab.gf

# Generate genmfc.gf mapping for HCopy input
go.genmfcgf genmfc.gf

# Run HCopy
HCopy -A -V -T 1 -C  ../config/gf.config.hcopy -S genmfc.gf > ../log/hcopy.gf.log
# Inspect them with HList
HList -h -e 1 mfc/1.mfc

# Do the Viterbi alg
ls ../datos-gf/mfc/*.mfc > testgf.scp
HVite -C ../config/config -H ../modelos/hmm-256-3/macros -H ../modelos/hmm-256-3/hmmdefs -S testgf.scp -l '*' -i recout-gf.mlf -w ../lm/wordnet.gf -p 0.0 -s 5.0 ../etc/dictgf ../etc/monophones+sil

# Show and count results
HResults -f -t -I ../etc/mlfwordsgf.test ../lm/vocab.gf recout-gf.mlf


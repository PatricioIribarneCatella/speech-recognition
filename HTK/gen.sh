#!/usr/bin/env bash

set -eu

dst=1

while read src; do
	echo $src "$dst".wav
	dst=$((dst + 1))
done


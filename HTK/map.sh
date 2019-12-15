#!/usr/bin/env bash

set -eu

while read src dst; do
	mv $src $dst
done


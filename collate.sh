#!/bin/bash

if [ -d _build ]; then
  rm -rf _build
fi

mkdir _build

cp -rf base_site/* _build/.

echo "H-Series"
gh release download -p hseries-docs-*  -R CQCL/hseries-documentation -D _build/
tar -xzf _build/hseries-docs-*.tar.gz -C _build/h-series

echo "Nexus"
gh release download -p nexus-docs-*.tar.gz -R CQCL-DEV/nexus-docs -D _build/ 
tar -xzf _build/nexus-docs-*.tar.gz -C _build/nexus

echo "TKET"
gh release download -p tket-docs-* -R CQCL-DEV/tket-site -D _build/
tar -xzf _build/tket-docs-*.tar.gz -C _build/tket

echo "InQuanto"
gh release download -p inquanto-docs-* -R CQCL-DEV/inquanto-docs -D _build/
tar -xzf _build/inquanto-docs-*.tar.gz -C _build/inquanto

echo "Lambeq"
gh release download -p lambeq-docs-* -R CQCL/lambeq-docs -D _build/
tar -xzf _build/lambeq-docs-*.tar.gz -C _build/lambeq

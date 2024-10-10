#!/bin/bash

echo "H-Series"
gh release download -p hseries-docs-*  -R CQCL/hseries-documentation -D base_site/
tar -xzf base_site/hseries-docs-*.tar.gz -C base_site/h-series

echo "Nexus"
gh release download -p nexus-docs-*.tar.gz -R CQCL-DEV/nexus-docs -D base_site/ 
tar -xzf base_site/nexus-docs-*.tar.gz -C base_site/nexus

echo "TKET"
gh release download -p tket-docs-* -R CQCL-DEV/tket-site -D base_site/
tar -xzf base_site/tket-docs-*.tar.gz -C base_site/tket

echo "InQuanto"
gh release download -p inquanto-docs-* -R CQCL-DEV/inquanto-docs -D base_site/
tar -xzf base_site/inquanto-docs-*.tar.gz -C base_site/inquanto

echo "Lambeq"
gh release download -p lambeq-docs-* -R CQCL/lambeq-docs -D base_site/
tar -xzf base_site/lambeq-docs-*.tar.gz -C base_site/lambeq

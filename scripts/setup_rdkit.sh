#!/bin/bash

set -e

VERSION="0.5.1"
URL="https://cdn.jsdelivr.net/npm/rdkit@${VERSION}/dist"
DIR="molcalc/static/rdkit"

mkdir -p ${DIR}
cd ${DIR}
wget -c ${URL}/RDKit_minimal.js
wget -c ${URL}/RDKit_minimal.wasm
mv RDKit_minimal.js rdkit.js
mv RDKit_minimal.wasm rdkit.wasm

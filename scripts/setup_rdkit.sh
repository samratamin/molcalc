#!/bin/bash

set -e

URL="https://unpkg.com/@rdkit/rdkit/dist"
DIR="molcalc/static/rdkit"

mkdir -p ${DIR}
cd ${DIR}
wget -c ${URL}/RDKit_minimal.js
wget -c ${URL}/RDKit_minimal.wasm
mv RDKit_minimal.js rdkit.js
mv RDKit_minimal.wasm rdkit.wasm

#!/bin/bash

set -e

URL="https://cdn.jsdelivr.net/npm/rdkit@0.5.1/dist/rdkit.js"
DIR="molcalc/static/rdkit"

mkdir -p ${DIR}
cd ${DIR}
wget -c ${URL} -O rdkit.js

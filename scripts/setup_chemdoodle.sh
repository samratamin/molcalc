#!/bin/bash

set -e

VERSION="11.0.0"
URL="https://web.chemdoodle.com/downloads/ChemDoodleWeb-${VERSION}.zip"
DIR="molcalc/static/chemdoodleweb"

mkdir -p ${DIR}
cd ${DIR}
wget -c ${URL}
unzip ChemDoodleWeb-*.zip
cp -r ChemDoodleWeb-${VERSION}/install/* .
cp -r ChemDoodleWeb-${VERSION}/src/* .
rm ChemDoodleWeb-*.zip
rm -r ChemDoodleWeb-${VERSION}

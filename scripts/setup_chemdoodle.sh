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
cp -r ChemDoodleWeb-${VERSION}/install/uis .

# Comment out the line that calls checkForUpdates
sed -i "s/.*iChemLabs.checkForUpdates.*/\/\/&/" ChemDoodleWeb-unpacked.js

rm ChemDoodleWeb-*.zip
rm -r ChemDoodleWeb-${VERSION}

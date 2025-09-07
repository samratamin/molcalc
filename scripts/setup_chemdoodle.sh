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

# Comment out the line that calls checkForUpdates
sed -i 's/checkForUpdates(this);/\/\/checkForUpdates(this);/' ChemDoodleWeb-unpacked.js

rm ChemDoodleWeb-*.zip
rm -r ChemDoodleWeb-${VERSION}

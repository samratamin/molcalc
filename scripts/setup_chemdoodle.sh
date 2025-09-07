#!/bin/bash

set -e

VERSION="11.0.0"
URL="https://web.chemdoodle.com/downloads/ChemDoodleWeb-${VERSION}.zip"
DIR="molcalc/static/chemdoodleweb"

# Clean up previous installs if they exist
rm -rf ${DIR}
mkdir -p ${DIR}
cd ${DIR}

echo "Downloading ChemDoodle..."
wget -c ${URL}
unzip -q ChemDoodleWeb-*.zip

echo "Copying ChemDoodle assets..."
# Copy all contents from the 'install' directory
cp -r ChemDoodleWeb-${VERSION}/install/* .

# The 'uis' components are loaded by a separate script tag. The 404 error
# from previous attempts suggests they may not be copied correctly by the
# wildcard. We will explicitly copy the 'uis' directory if it exists at the
# root of the unzipped folder.
if [ -d "ChemDoodleWeb-${VERSION}/uis" ]; then
    echo "Found 'uis' directory in root, copying..."
    cp -r ChemDoodleWeb-${VERSION}/uis .
fi

# Also copy src files, they might contain necessary components.
cp -r ChemDoodleWeb-${VERSION}/src/* .

echo "Patching ChemDoodle to prevent CORS errors..."
# This is a critical step. The checkForUpdates function causes CORS issues.
# Previous attempts to comment out the line caused syntax errors. This final
# attempt simply deletes the line containing the function call.
sed -i '/checkForUpdates/d' ChemDoodleWeb-unpacked.js

echo "Cleaning up..."
rm ChemDoodleWeb-*.zip
rm -r ChemDoodleWeb-${VERSION}

echo "ChemDoodle setup complete."

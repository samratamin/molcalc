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

# The 'uis' components are loaded by a separate script tag, but it seems they
# are located inside the 'install' directory as well. The 404 error suggests
# they might not be copied correctly by the wildcard. We will try to find
# the uis directory and copy it to the root.
# A common location for this is in the root of the unzipped folder or inside 'src'.
if [ -d "ChemDoodleWeb-${VERSION}/uis" ]; then
    echo "Found 'uis' directory in root, copying..."
    cp -r ChemDoodleWeb-${VERSION}/uis .
elif [ -d "uis" ]; then
    echo "'uis' directory already copied, skipping."
else
    echo "Warning: 'uis' directory not found. The ChemDoodle UI might not work correctly."
fi

# Also copy src files, they might contain necessary components.
cp -r ChemDoodleWeb-${VERSION}/src/* .

echo "Patching ChemDoodle to prevent CORS errors..."
# This is a critical step. The checkForUpdates function causes CORS issues when
# the app is not running on a public domain. We comment out the line that calls it.
# We use a general regex to catch the line even if there is whitespace.
sed -i '/.*checkForUpdates.*/s/^/\/\//' ChemDoodleWeb-unpacked.js

echo "Cleaning up..."
rm ChemDoodleWeb-*.zip
rm -r ChemDoodleWeb-${VERSION}

echo "ChemDoodle setup complete."

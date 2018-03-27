#!/bin/sh
cd ..

DEST=yeti@yeticam:/home/yeti

echo "Creating Directories..."
mkdir -p _dist/yeti/cam
mkdir -p _dist/yeti/common

echo "Copying setup"
cp -a utilities/{setup.sh,yeticam.service,yeticam.environment} _dist/

echo "Copying application"
cp -a yeti/common/*.py _dist/yeti/common/
cp -a yeti/cam/*.py _dist/yeti/cam/
cp -a yeti/*.py _dist/yeti/
cp -a cam.py _dist/

echo "Sending to device"
scp -r _dist/* $DEST

echo "Cleaning up"
rm -r _dist


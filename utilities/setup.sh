#!/usr/bin/env bash

# Install 3rd party python packages

sudo pip install ...

# Set permissions

chmod +x /home/yeti/cam.py

# Install service

sudo cp yeticam.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/yeticam.service
sudo systemctl daemon-reload
sudo systemctl enable yeticam.service
sudo systemctl start yeticam.service

# Add crontab to reboot daily at 2:09am (minutes staggered so multiple cams aren't sending on the same cadence)

sudo crontab -l | { cat; echo "9 2 0 0 0 reboot"; } | crontab -
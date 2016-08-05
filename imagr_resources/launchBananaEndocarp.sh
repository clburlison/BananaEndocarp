#!/bin/bash

/usr/bin/hdiutil mount -quiet -nobrowse "http://server/dmgs/BananaEndocarp.dmg"
/Volumes/BananaEndocarp/BananaEndocarp.py
/usr/bin/hdiutil unmount /Volumes/BananaEndocarp
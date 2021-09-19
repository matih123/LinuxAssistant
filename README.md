# LinuxAssistant
Available on android (> 4.0).

## Download .apk from 
https://mega.nz/folder/IEN2FRiK#Wchyr5oqr640kB_sxA5yDw

## General information
Android app made in python kivy for managing linux servers.

App contains modules:
* general information
* raspberrypi information
* automated screenshot

Work in progress:
* speedtest in general panel
* websites status
* linux services status
* packages updates

App connects to ssh using paramiko python module and reads information using linux commands from utils.py file.

Raspberry module can be turned on when connecting to raspberry pi with bme280 and hc-sr04 sensors. Managing script for bme280 has to be placed in Desktop/bme.py (path after logging to ssh) and has to return temperature, pressure, humidity separated by new line. Managing script for hc-sr04 has to be placed in Desktop/hc.py (path after logging to ssh) and what it returns is directly displayed in DISTANCE box.

Refresh rate and language (available: Polish and English) can be changed in config file.

## Setup
App needs following android permissions: INTERNET, ACCESS_NETWORK_STATE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE.

After first run config file will be created in /storage/emulated/0/Documents/config.ini.

In config [SSH] section login credentials to your linux server should be entered.

## Overview
![app overview image](img/overview.jpg?raw=true "Title")

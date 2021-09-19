# LinuxAssistant
Available on android (> 4.0) and linux.

# General information
Linux and android app made in python kivy for managing linux servers.

App contains modules:
* general information
* raspberrypi information
* automated screenshot

Work in progress:
* websites status
* linux services status
* packages updates

# Setup
App needs following android permissions: INTERNET, ACCESS_NETWORK_STATE, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE.

After first run config file will be created (on android: /storage/emulated/0/Documents/config.ini).

In config [SSH] section login credentials to your linux server should be entered.

App connects to ssh using paramiko python module and reads information using linux commands from utils.py file.

Raspberry module can be turned on when connecting to raspberry pi with bme280 sensor. Managing script has to be placed in Desktop/bme.py (path after logging to ssh) and has to return temperature, pressure, humidity separated by new line.

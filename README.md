# Hubitat-Bluetooth-Sensor

python program to sense bluetooth MAC addresses. NOTE: I haven't gotten this working with iPhone devices becuase Apple disables any sort of scanning unless it is running in the foreground. This has only been successfully tested with Android devices.

## Installation

If you are using something other than a rapsberry pi, install the following dependencies:

- bluetooth
- peewee
- sqlite3

If you are planning to run this on a raspberry pi running a linux OS, run the following commands:

- `sudo apt update && sudo apt upgrade -y`
- `sudo apt-get install python3-pip` OR `sudo apt-get install python-pip`
- `sudo apt install -y bluetooth libusb-dev libdbus-1-dev libglib2.0-dev libudev-dev libical-dev libreadline-dev bluez python-bluez sqlite3`
- `pip3 install peewee` OR `pip install peewee`

BEFORE FIRST RUN:

- clone this repository
- go to your Hubitat -> Drivers Code -> New Driver
- copy and paste the code from [Virtual Phone Presence Plus.groovy](https://raw.githubusercontent.com/AJax2012/Hubitat-Bluetooth-Sensor/master/Virtual%20Phone%20Presence%20Plus.groovy) into the New Driver page. You can also just copy the link and click Import. NOTE: DO NOT CHANGE THE DRIVER NAME. It is hard-coded into sensor.py. If you need to change it, you will have to change the name manually in sensor.py on line 68 (subject to change).
- Create your devices using the new driver
- If you don't know the bluetooth mac address for your device, run `python sensor-test.py` to find all devices in range.
- Once you have your BT mac address, copy and paste it into the Device BT Mac Addr in your new device's Preferences section. Repeat for each device you want to track.
- Edit sensor.py Hubitat data. Around lines 47 - 51 have inline-instructions (note that the lines may change and this may be out of date).
- Run the program using `python sensor.py` or `python3 sensor.py`. Once you run it, it will create a Sqlite3 database with your hub information, devices, and device statuses.

## Notes

This hasn't been tested on anything other than a raspberry pi. I will not be providing support directly for other devices.
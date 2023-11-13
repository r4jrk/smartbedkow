# SmartBedkow

An automation tool to toggle on/off Tuya-controlled radiators based on
current photovoltaics power production (based on SolarEdge Inverter data).

## Description

SmartBedkow is an automation software that utilizes the SolarEdge API to 
gather the photovoltaic panels power production and, based on the specified 
thresholds (in settings.cfg), turns on or off the Tuya-controlled radiators 
connected to the local network (via Wi-Fi). The control device running 
the software (in principle Raspberry Pi) does not need to be connected to 
the Internet.

A minimum temperature threshold in settings.cfg overrides the power production 
threshold. Meaning, in case of temperature read by sensor on any of the radiators 
in local network to be lower than specified, regardless of the power production, 
the turn on command will be sent to the radiators.

## Prerequisites

### SolarEdge-related stuff

1. API Key. Example: `TO1URAJ0ABD6NAUI52VMOA363N4C3UB7`.
2. Site ID. Example: `2431166`.

You can get it from Admin panel in [SolarEdge Monitoring](https://monitoring.solaredge.com/),
though since I was missing it, I got the API Key(s) and Site ID(s) from SolarEdge Support. 

### Tuya-related stuff

1. API Key a.k.a. Access ID/Client. Example: `4je3h7mbpj1b01uz86zj`.
2. Access Secret. Example: `9ce23c69e36d46ad961a2d0bf8dg8786`.
3. Example Device ID. Example: `1210444798b4afdf3324`.

API Key and Access Secret can be gathered from [Tuya IoT Cloud](https://iot.tuya.com/cloud)
in Project screen under Authorization Key. Device IDs can be fetched using 
TinyTuya scan (described under [How to run it?](#how-to-run-it)).

### Software

* Python 2 or 3.
* TinyTuya Python module [TinyTuya GitHub](https://github.com/jasonacox/tinytuya).
To install, execute "python -m pip install tinytuya" in Terminal.

## How to run it?

1. Run the TinyTuya Wizard to get the devices' Local Keys. Please refer to:
[TinyTuya GitHub Getting Local Keys](https://github.com/jasonacox/tinytuya#setup-wizard---getting-local-keys)
2. Set up Tuya Developer Account (please open the aforementioned link and follow the steps described there).
3. Connect to the network the radiators are connected to.
4. Run the following command in Terminal: `python -m tinytuya scan` to scan the network to reveal
the connected devices and to get their local IP addresses. The "snapshot.json" file will be created.
5. Use the gathered data from [snapshot.json](snapshot.json) and populate the [devices.csv](devices.csv) file.
6. Populate [settings.cfg](settings.cfg) with desired thresholds, SolarEdge API Key and Site ID.
7. Run SmartBedkow using the following command in Terminal (opened in project's directory): `python main.py --start`
   (you may also wish to see the help by invoking `python main.py --help`).

## Important!

As of now, invoking the main.py with --stop parameter will only stop the program on Linux-based OSes.

## How to change the network settings on Raspberry Pi?

1. Open text editor and paste the following lines:
    `country=US
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    network={
    ssid="YOURSSID"
    scan_ssid=1
    psk="YOURPASSWORD"
    key_mgmt=WPA-PSK
    }`

2. For the `ssid` and `psk` keys put appropriate values. Change the ISO country code, if needed. 
3. Save the file as `wpa_supplicant.conf`. Plug the Raspberry Pi SD Card to your PC. 
4. Copy the newly created file to the boot partition on SD Card. 
5. Plug the card into the Raspberry Pi and boot it. 
6. Done. 

# Feel free to contribute!
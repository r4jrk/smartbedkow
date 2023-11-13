import configparser
import datetime
import tinytuya
import solar_edge
import tuya_smart
import logging
import sys

DEVICES = []

DEVICE_DATA_FILE_NAME = "devices.csv"
CONFIG_FILE_NAME = "settings.cfg"

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    handlers=[
                        logging.StreamHandler(sys.stdout)
                    ])

print("Starting to determine SolarEdge endpoint using data from %s..." % CONFIG_FILE_NAME)

with open(CONFIG_FILE_NAME, "r") as settings:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_NAME)
    solar_edge_api_key = config["SETTINGS"]["solar_edge_api_key"]
    solar_edge_site_id = config["SETTINGS"]["solar_edge_site_id"]
    SOLAR_EDGE_API_START_TIME = datetime.datetime.now()
    SOLAR_EDGE_API_END_TIME = datetime.datetime.now()

    if len(solar_edge_api_key) == 0:
        logging.critical("SolarEdge API Key is empty. SmartBedkow will stop processing")
        logging.warning("S M A R T B E D K O W   S T O P P E D")
        sys.exit()

    if len(solar_edge_site_id) == 0:
        logging.critical("SolarEdge SITE Id is empty. SmartBedkow will stop processing")
        logging.warning("S M A R T B E D K O W   S T O P P E D")
        sys.exit()

    se = solar_edge.SolarEdge(solar_edge_api_key, solar_edge_site_id, SOLAR_EDGE_API_START_TIME, SOLAR_EDGE_API_END_TIME)

    se.build_solar_edge_api_uri()

print()

# url = "https://openapi.tuyaeu.com/v2.0/cloud/thing/40631580483fda1abcab/shadow/properties?codes=Temp_current"
# headers = {"sign_method": "HMAC-SHA256", "client_id": "4je3h7mpbj1bo1uj86zj",
# "t": "1699561886811", "mode": "cors", "Content-Type": "application/json",
# "sign": "sign,
# "access_token": "9ec23c69e63d46ad961a0d0bf8dc8286"}
# r = requests.get(url, headers=headers)

# print(r.json())

# name = "Test radiator"
# id = DEVICES_CONFIGURATION[i].get("id").strip()
# ip_address = DEVICES_CONFIGURATION[i].get("ip_address").strip()
# local_key = DEVICES_CONFIGURATION[i].get("local_key").strip()
# device = tuya_smart.TuyaSmart(name, id, ip_address, local_key)

print()

print("Starting to parse data from %s..." % DEVICE_DATA_FILE_NAME)

with open(DEVICE_DATA_FILE_NAME, "r") as devices:
    for line in devices:
        contents = line.split(",")
        read_code = 0
        if contents[0] == "no":     # To omit headers
            continue
        row_number = contents[0]
        name = contents[1]
        id = contents[2]
        ip_address = contents[3]
        local_key = contents[4]
        if (name != "") & (id != "") & (ip_address != "") & (local_key != ""):
            if len(ip_address.split(".")) != 4:
                print("IP address for %s read from row %s in %s is invalid." % (name, row_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
            if len(id) != 20:
                print("Device ID for %s read from row %s in %s is invalid." % (name, row_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
            if len(local_key) != 17:
                print("Device local key for %s read from row %s in %s is invalid." % (name, row_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
        else:
            print("Data in row %s in %s is not complete. Skipping..." % (row_number, DEVICE_DATA_FILE_NAME))
            continue

        if read_code != 0:
            print("Device data for %s (row %s in %s) seem to be invalid. Device will not be initialized." % (name, row_number, DEVICE_DATA_FILE_NAME))
        else:
            DEVICES.append({"row_number": row_number, "name": name, "id": id,
                            "ip_address": ip_address, "local_key": local_key})

print("Parsing data from %s finished." % DEVICE_DATA_FILE_NAME)

print(DEVICES[0].get("name"))

d = tinytuya.OutletDevice(
    dev_id=DEVICES[0].get("id"),
    address=DEVICES[0].get("ip_address"),
    local_key=DEVICES[0].get("local_key"),
    version=3.3)


name = DEVICES[0].get("name").strip()
id = DEVICES[0].get("id").strip()
ip_address = DEVICES[0].get("ip_address").strip()
local_key = DEVICES[0].get("local_key").strip()

print("id: " + id + ", ip_address: " + ip_address + ", local_key: " + local_key)

device = tuya_smart.TuyaSmart(name, id, ip_address, local_key)

print("Current temperature near " + name + "is " + str(device.get_current_temperature()))

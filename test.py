import configparser
import datetime
import solar_edge

DEVICES = []

DEVICE_DATA_FILE_NAME = "devices.csv"
CONFIG_FILE_NAME = "settings.cfg"

print("Starting to determine SolarEdge endpoint using data from %s..." % CONFIG_FILE_NAME)

with open(CONFIG_FILE_NAME, "r") as settings:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_NAME)
    solar_edge_api_key = config["SETTINGS"]["solar_edge_api_key"]
    solar_edge_site_id = config["SETTINGS"]["solar_edge_site_id"]
    SOLAR_EDGE_API_START_TIME = datetime.datetime.now()
    SOLAR_EDGE_API_END_TIME = datetime.datetime.now()

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

# device_name = "Test radiator"
# device_id = DEVICES_CONFIGURATION[i].get("device_id").strip()
# device_ip_address = DEVICES_CONFIGURATION[i].get("device_ip_address").strip()
# device_local_key = DEVICES_CONFIGURATION[i].get("device_local_key").strip()
# device = tuya_smart.TuyaSmart(device_name, device_id, device_ip_address, device_local_key)

print()

print("Starting to parse data from %s..." % DEVICE_DATA_FILE_NAME)

with open(DEVICE_DATA_FILE_NAME, "r") as devices:
    for line in devices:
        contents = line.split(",")
        read_code = 0
        if contents[0] == "no":     # To omit headers
            continue
        row_number = contents[0]
        device_name = contents[1]
        device_id = contents[2]
        device_ip_address = contents[3]
        device_local_key = contents[4]
        if (device_name != "") & (device_id != "") & (device_ip_address != "") & (device_local_key != ""):
            if len(device_ip_address.split(".")) != 4:
                print("IP address for %s read from row %s in %s is invalid." % (device_name, row_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
            if len(device_id) != 20:
                print("Device ID for %s read from row %s in %s is invalid." % (device_name, row_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
            if len(device_local_key) != 17:
                print("Device local key for %s read from row %s in %s is invalid." % (device_name, row_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
        else:
            print("Data in row %s in %s is not complete. Skipping..." % (row_number, DEVICE_DATA_FILE_NAME))
            continue

        if read_code != 0:
            print("Device data for %s (row %s in %s) seem to be invalid. Device will not be initialized." % (device_name, row_number, DEVICE_DATA_FILE_NAME))
        else:
            DEVICES.append({"row_number": row_number, "device_name": device_name, "device_id": device_id,
                            "device_ip_address": device_ip_address, "device_local_key": device_local_key})

print("Parsing data from %s finished." % DEVICE_DATA_FILE_NAME)

print(DEVICES[0].get("device_name"))
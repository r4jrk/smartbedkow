DEVICES = []

DEVICE_DATA_FILE_NAME = "urzadzenia.csv"

print("Starting to parse data from %s..." % DEVICE_DATA_FILE_NAME)
with open(DEVICE_DATA_FILE_NAME, "r") as urzadzenia:
    for line in urzadzenia:
        contents = line.split(",")
        read_code = 0
        if contents[0] == "lp":     # To omit headers
            continue
        line_number = contents[0]
        device_name = contents[1]
        device_id = contents[2]
        device_ip_address = contents[3]
        device_local_key = contents[4]
        if (device_name != "") & (device_id != "") & (device_ip_address != "") & (device_local_key != ""):
            if len(device_ip_address.split(".")) != 4:
                print("IP address for %s read from row %s in %s is invalid." % (device_name, line_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
            if len(device_id) != 20:
                print("Device ID for %s read from row %s in %s is invalid." % (device_name, line_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
            if len(device_local_key) != 17:
                print("Device local key for %s read from row %s in %s is invalid." % (device_name, line_number, DEVICE_DATA_FILE_NAME))
                read_code = 1
        else:
            print("Data in row %s in %s is not complete. Skipping..." % (line_number, DEVICE_DATA_FILE_NAME))
            continue

        if read_code != 0:
            print("Device data for %s (row %s in %s) seem to be invalid. Device will not be initialized." % (device_name, line_number, DEVICE_DATA_FILE_NAME))
        else:
            DEVICES.append({"line_number": line_number, "device_name": device_name, "device_id": device_id,
                            "device_ip_address": device_ip_address, "device_local_key": device_local_key})

print("Parsing data from %s finished." % DEVICE_DATA_FILE_NAME)

print(DEVICES[0].get("device_name"))
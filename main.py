import configparser
import datetime
import logging
import os
import platform
import sys
import time
import solar_edge
import tuya_smart

# SOLAR EDGE
SOLAR_EDGE_API_START_TIME = datetime.datetime.now()
SOLAR_EDGE_API_END_TIME = datetime.datetime.now()

DEVICES_CONFIGURATION = []
DEVICES = []

CONFIG_FILE_NAME = "settings.cfg"
DEVICE_DATA_FILE_NAME = "devices.csv"
LOGNAME = "smartbedkow.log"


def get_app_configuration_from_file():
    logging.info("Reading configuration from %s..." % CONFIG_FILE_NAME)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_NAME)
    solar_edge_api_key = config["SETTINGS"]["solar_edge_api_key"]
    solar_edge_site_id = config["SETTINGS"]["solar_edge_site_id"]
    wattage_threshold = config["SETTINGS"]["minimal_power_produced_to_turn_on_radiators_in_watts"]
    logging.info("Wattage threshold read from configuration file: %s W" % wattage_threshold)
    temperature_threshold = config["SETTINGS"]["low_temperature_wattage_threshold_override_in_celsius"]
    logging.info("Temperature threshold read from configuration file: %s °C" % temperature_threshold)
    refresh_interval = config["SETTINGS"]["refresh_rate_in_seconds"]
    logging.info("Refresh interval read from configuration file: %s s" % refresh_interval)
    return {"solar_edge_api_key": solar_edge_api_key,
            "solar_edge_site_id": solar_edge_site_id,
            "wattage_threshold": wattage_threshold,
            "temperature_threshold": temperature_threshold,
            "refresh_interval": refresh_interval}


def get_device_configuration_from_file():
    logging.info("Starting to parse data from %s..." % DEVICE_DATA_FILE_NAME)
    with open(DEVICE_DATA_FILE_NAME, "r") as file:
        for line in file:
            row_contents = line.split(",")
            if row_contents[0] == "no":  # To omit headers
                continue
            row_number = row_contents[0]
            name = row_contents[1]
            id = row_contents[2]
            ip_address = row_contents[3]
            local_key = row_contents[4]
            if (name != "") & (id != "") & (ip_address != "") & (local_key != ""):
                if len(ip_address.split(".")) != 4:
                    logging.info("IP address for %s read from row %s in %s is invalid." % (name, row_number,
                                                                                           DEVICE_DATA_FILE_NAME))
                if len(id) != 20:
                    logging.info("Device ID for %s read from row %s in %s is invalid." % (name, row_number,
                                                                                          DEVICE_DATA_FILE_NAME))
                if len(local_key) != 17:
                    logging.info(
                        "Device local key for %s read from row %s in %s is invalid." % (name, row_number,
                                                                                        DEVICE_DATA_FILE_NAME))
            else:
                logging.warning(
                    "Data in row %s in %s is not complete. Skipping..." % (row_number, DEVICE_DATA_FILE_NAME))
                continue

            DEVICES_CONFIGURATION.append({"row_number": row_number, "name": name, "id": id,
                                          "ip_address": ip_address, "local_key": local_key})

    logging.info("Parsing data from %s finished" % DEVICE_DATA_FILE_NAME)


def get_input_parameters():
    args = sys.argv
    i = 0
    for arg in args:
        if len(args) == 1:
            print("No argument was specified. Accepted parameters: --start, --stop, --help")
            sys.exit(0)

        i = i + 1  # To omit MAIN.PY argument
        if i == 1:
            continue

        arg = arg.upper()

        if arg in ("START", "--START"):
            start()
        elif arg in ("STOP", "--STOP"):
            stop()
        elif arg in ("HELP", "--HELP"):
            print("This is SmartBedkow. Accepts following parameters: --start, --stop and --help.")
            print("     Starting application with --start parameter will start the program.")
            print("     Starting application with --stop parameter will stop the program.")
            print("     Starting application with --help parameter will display the message you are reading right now.")
            print(
                "                                                                                    - Rafał, 05/05/2022.")
        else:
            print("Unknown argument: %s. Accepted parameters: --start, --stop, --help" % args[1])
            sys.exit(0)


def start():
    print_smart_bedkow()
    logging.warning("S T A R T I N G   S M A R T B E D K O W")

    app_config = get_app_configuration_from_file()

    refresh_interval_in_seconds = int(app_config["refresh_interval"])
    refresh_interval_in_minutes = refresh_interval_in_seconds / 60
    wattage_threshold = int(app_config["wattage_threshold"])
    temperature_threshold = int(app_config["temperature_threshold"])
    solar_edge_api_key = app_config["solar_edge_api_key"]
    solar_edge_site_id = app_config["solar_edge_site_id"]

    if len(solar_edge_api_key) == 0:
        logging.critical("SolarEdge API Key is empty. SmartBedkow will stop processing")
        logging.warning("S M A R T B E D K O W   S T O P P E D")
        sys.exit()

    if len(solar_edge_site_id) == 0:
        logging.critical("SolarEdge SITE Id is empty. SmartBedkow will stop processing")
        logging.warning("S M A R T B E D K O W   S T O P P E D")
        sys.exit()

    get_device_configuration_from_file()

    logging.info("%s device(s) will be attempted to be initialized" % len(DEVICES_CONFIGURATION))

    device_initialized = False

    for i in range(len(DEVICES_CONFIGURATION)):
        name = DEVICES_CONFIGURATION[i].get("name").strip()
        id = DEVICES_CONFIGURATION[i].get("id").strip()
        ip_address = DEVICES_CONFIGURATION[i].get("ip_address").strip()
        local_key = DEVICES_CONFIGURATION[i].get("local_key").strip()
        device = tuya_smart.TuyaSmart(name, id, ip_address, local_key)
        if device.is_initialized():
            device_initialized = True
        DEVICES.append(device)

    if not device_initialized:
        logging.critical("No device was initialized. SmartBedkow will stop processing")
        logging.warning("S M A R T B E D K O W   S T O P P E D")
        sys.exit()
    else:
        logging.info("Device(s) initialization completed")

    se = solar_edge.SolarEdge(solar_edge_api_key, solar_edge_site_id, SOLAR_EDGE_API_START_TIME,
                              SOLAR_EDGE_API_END_TIME)

    logging.warning("S M A R T B E D K O W   S T A R T E D")

    while True:
        se.update_times(time_interval=refresh_interval_in_minutes)
        se.get_solar_edge_api_response()

        se_power_production = se.get_power_production()
        if se_power_production >= wattage_threshold:  # Turn on radiators
            for device in DEVICES:
                if device.is_initialized():
                    if not device.is_on():
                        device.turn_on()
        else:  # Turn off radiator(s) unless the measured temperature is no less than the threshold
            for device in DEVICES:
                if device.is_initialized():
                    if device.get_current_temperature() <= temperature_threshold:
                        if not device.is_on():
                            device.turn_on()
                    else:
                        device.turn_off()

        time.sleep(refresh_interval_in_seconds)  # Run every SOLAR_EDGE_POWER_PRODUCTION_REFRESH_INTERVAL_IN_SECONDS / 60 minutes


def stop():
    # Linux only
    if platform.system() == "Linux":
        logging.info("Program stopped by " + os.getlogin())
        os.system('ps axf | grep main | grep -v grep | awk \'{print "kill -9 " $1 }\' | sh')
    else:
        print("This command will not work on OS other than Linux")


def print_smart_bedkow():
    print("")
    print(        "   .-'''-. ,---.    ,---.   ____    .-------. ,---------.  _______       .-''-.   ______     .--.   .--.      ,-----.    .--.      .--. ")
    print(        "  / _     \|    \  /    | .'  __ `. |  _ _   \\\          \\\  ____  \   .'_ _   \ |    _ `''. |  | _/  /     .'  .-,  '.  |  |_     |  | ")
    print(        " (`' )/`--'|  ,  \/  ,  |/   '  \  \| ( ' )  | `--.  ,---'| |    \ |  / ( ` )   '| _ | ) _  \| (`' ) /     / ,-.|  \ _ \ | _( )_   |  | ")
    print(        "(_ o _).   |  |\_   /|  ||___|  /  ||(_ o _) /    |   \   | |____/ / . (_ o _)  ||( ''_'  ) ||(_ ()_)     ;  \  '_ /  | :|(_ o _)  |  | ")
    print(        " (_,_). '. |  _( )_/ |  |   _.-`   || (_,_).' __  :_ _:   |   _ _ '. |  (_,_)___|| . (_) `. || (_,_)   __ |  _`,/ \ _/  || (_,_) \ |  | ")
    print(        ".---.  \  :| (_ o _) |  |.'   _    ||  |\ \  |  | (_I_)   |  ( ' )  \\'  \   .---.|(_    ._) '|  |\ \  |  |: (  '\_/ \   ;|  |/    \|  | ")
    print(        "\    `-'  ||  (_,_)  |  ||  _( )_  ||  | \ `'   /(_(=)_)  | (_{;}_) | \  `-'    /|  (_.\.' / |  | \ `'   / \ `"'"/  \  ) / |  '  "'"' '" /\  `  | ")
    print(        " \       / |  |      |  |\ (_ o _) /|  |  \    /  (_I_)   |  (_,_)  /  \       / |       .'  |  |  \    /   '. \_/``"'"''.'"'""  |    /  \    | ")
    print(        "  `-...-'  '--'      '--' '.(_,_).' ''-'   `'-'   '---'   /_______.'    `'-..-'  '-----'`    `--'   `'-'      '-----'    `---'    `---` ")
    print("")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        handlers=[
                            logging.FileHandler(LOGNAME),
                            logging.StreamHandler(sys.stdout)
                        ])
    get_input_parameters()

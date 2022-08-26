import configparser
import datetime
import logging
import os
import sys
import time
import readchar as readchar
import solar_edge
import tuya_smart

# SOLAR EDGE
SOLAR_EDGE_API_KEY = "TO0UVRJ0AEV3NAUI52VMOOD63NVCDEBD"
SOLAR_EDGE_API_START_TIME = datetime.datetime.now()
SOLAR_EDGE_API_END_TIME = datetime.datetime.now()

DEVICES_CONFIGURATION = []
DEVICES = []

CONFIG_FILE_NAME = "ustawienia.cfg"
DEVICE_DATA_FILE_NAME = "urzadzenia.csv"
LOGNAME = "smartbedkow.log"


def get_app_configuration_from_file():
    logging.info("Reading configuration from %s..." % CONFIG_FILE_NAME)
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_NAME)
    wattage_threshold = config["USTAWIENIA"]["minimalna_produkcja_do_wlaczenia_grzejnikow"]
    logging.info("Wattage threshold read from configuration file: %s W" % wattage_threshold)
    refresh_interval = config["USTAWIENIA"]["czestotliwosc_odswiezania_w_sekundach"]
    logging.info("Refresh interval read from configuration file: %s s" % refresh_interval)
    return {"wattage_threshold": wattage_threshold, "refresh_interval": refresh_interval}


def get_device_configuration_from_file():
    logging.info("Starting to parse data from %s..." % DEVICE_DATA_FILE_NAME)
    with open(DEVICE_DATA_FILE_NAME, "r") as file:
        for line in file:
            line_contents = line.split(",")
            if line_contents[0] == "lp":  # To omit headers
                continue
            line_number = line_contents[0]
            device_name = line_contents[1]
            device_id = line_contents[2]
            device_ip_address = line_contents[3]
            device_local_key = line_contents[4]
            if (device_name != "") & (device_id != "") & (device_ip_address != "") & (device_local_key != ""):
                if len(device_ip_address.split(".")) != 4:
                    logging.info("IP address for %s read from row %s in %s is invalid." % (device_name, line_number,
                                                                                           DEVICE_DATA_FILE_NAME))
                if len(device_id) != 20:
                    logging.info("Device ID for %s read from row %s in %s is invalid." % (device_name, line_number,
                                                                                          DEVICE_DATA_FILE_NAME))
                if len(device_local_key) != 17:
                    logging.info("Device local key for %s read from row %s in %s is invalid." % (device_name, line_number,
                                                                                                 DEVICE_DATA_FILE_NAME))
            else:
                logging.warning("Data in row %s in %s is not complete. Skipping..." % (line_number, DEVICE_DATA_FILE_NAME))
                continue

            DEVICES_CONFIGURATION.append({"line_number": line_number, "device_name": device_name, "device_id": device_id,
                                          "device_ip_address": device_ip_address, "device_local_key": device_local_key})

    logging.info("Parsing data from %s finished" % DEVICE_DATA_FILE_NAME)


def get_input_parameters():
    args = sys.argv
    i = 0
    for arg in args:
        i = i + 1       # To omit MAIN.PY argument
        if i == 1:
            continue

        arg = arg.upper()

        if len(args) == 1:
            print("No argument was specified. Accepted parameters: -start, -stop, -help")
            print("Press any key to exit...")
            readchar.readchar()
            sys.exit(0)

        if arg in ("START", "-START"):
            start()
        elif arg in ("STOP", "-STOP"):
            stop()
        elif arg in ("HELP", "-HELP"):
            print("Ten program to SmartBedkow. Przyjmuje parametry -start, -stop i -help.")
            print("     Uruchomienie programu z parametrem -start spowoduje uruchomienie programu.")
            print("     Uruchomienie programu z parametrem -stop spowoduje jego zatrzymanie.")
            print("     Uruchomienie programu z parametrem -help spowoduje wyświetlenie komunikatów, które właśnie czytasz.")
            print("                                                                                    - Rafał, 05/05/2022.")
        else:
            print("Unknown argument: %s. Accepted parameters: -start, -stop, -help" % args[1])


def start():
    logging.warning("S T A R T I N G   S M A R T B E D K O W")

    app_config = get_app_configuration_from_file()

    refresh_interval_in_seconds = int(app_config["refresh_interval"])
    refresh_interval_in_minutes = refresh_interval_in_seconds / 60
    wattage_threshold = int(app_config["wattage_threshold"])

    get_device_configuration_from_file()

    logging.info("%s device(s) will be initialized" % len(DEVICES_CONFIGURATION))

    device_initialized = False

    for i in range(len(DEVICES_CONFIGURATION)):
        device_name = DEVICES_CONFIGURATION[i].get("device_name").strip()
        device_id = DEVICES_CONFIGURATION[i].get("device_id").strip()
        device_ip_address = DEVICES_CONFIGURATION[i].get("device_ip_address").strip()
        device_local_key = DEVICES_CONFIGURATION[i].get("device_local_key").strip()
        device = tuya_smart.TuyaSmart(device_name, device_id, device_ip_address, device_local_key)
        if device.is_initialized():
            device_initialized = True
        DEVICES.append(device)

    if not device_initialized:
        logging.critical("No device was initialized. SmartBedkow will stop processing")
        logging.warning("S M A R T B E D K O W   S T O P P E D")
        sys.exit()
    else:
        logging.info("Device(s) initialization completed")

    se = solar_edge.SolarEdge(SOLAR_EDGE_API_KEY, SOLAR_EDGE_API_START_TIME, SOLAR_EDGE_API_END_TIME)

    logging.warning("S M A R T B E D K O W   S T A R T E D")

    # i = 0
    while True:
        # Trzeba będzie zrobić konfigurację (tinytuya wizard) na Będkowie.

        se.update_times(time_interval=refresh_interval_in_minutes)
        se.get_solar_edge_api_response()

        se_power_production = se.get_power_production()
        if se_power_production >= wattage_threshold:  # Turn on radiators
            for device in DEVICES:
                if not device.is_on():
                    if device.is_initialized():
                        device.turn_on()
        else:  # Turn off radiators
            for device in DEVICES:
                if device.is_on():
                    if device.is_initialized():
                        device.turn_off()

#########################################
        #USUNĄĆ PO TESTACH
        # i = i + 1
        # if i % 2 == 0:
        #     radiator1.turn_off()
        # else:
        #     radiator1.turn_on()

#########################################

        time.sleep(refresh_interval_in_seconds)  # Run every SOLAR_EDGE_POWER_PRODUCTION_REFRESH_INTERVAL_IN_SECONDS / 60 minutes


def stop():
    logging.info("Program stopped by " + os.getlogin())
    os.system('ps axf | grep main | grep -v grep | awk \'{print "kill -9 " $1 }\' | sh')


def print_smart_bedkow():
    print("")
    print("   .-'''-. ,---.    ,---.   ____    .-------. ,---------.  _______       .-''-.   ______     .--.   .--.      ,-----.    .--.      .--. ")
    print("  / _     \|    \  /    | .'  __ `. |  _ _   \\\          \\\  ____  \   .'_ _   \ |    _ `''. |  | _/  /     .'  .-,  '.  |  |_     |  | ")
    print(" (`' )/`--'|  ,  \/  ,  |/   '  \  \| ( ' )  | `--.  ,---'| |    \ |  / ( ` )   '| _ | ) _  \| (`' ) /     / ,-.|  \ _ \ | _( )_   |  | ")
    print("(_ o _).   |  |\_   /|  ||___|  /  ||(_ o _) /    |   \   | |____/ / . (_ o _)  ||( ''_'  ) ||(_ ()_)     ;  \  '_ /  | :|(_ o _)  |  | ")
    print(" (_,_). '. |  _( )_/ |  |   _.-`   || (_,_).' __  :_ _:   |   _ _ '. |  (_,_)___|| . (_) `. || (_,_)   __ |  _`,/ \ _/  || (_,_) \ |  | ")
    print(".---.  \  :| (_ o _) |  |.'   _    ||  |\ \  |  | (_I_)   |  ( ' )  \\'  \   .---.|(_    ._) '|  |\ \  |  |: (  '\_/ \   ;|  |/    \|  | ")
    print("\    `-'  ||  (_,_)  |  ||  _( )_  ||  | \ `'   /(_(=)_)  | (_{;}_) | \  `-'    /|  (_.\.' / |  | \ `'   / \ `"'"/  \  ) / |  '  "'"' '" /\  `  | ")
    print(" \       / |  |      |  |\ (_ o _) /|  |  \    /  (_I_)   |  (_,_)  /  \       / |       .'  |  |  \    /   '. \_/``"'"''.'"'""  |    /  \    | ")
    print("  `-...-'  '--'      '--' '.(_,_).' ''-'   `'-'   '---'   /_______.'    `'-..-'  '-----'`    `--'   `'-'      '-----'    `---'    `---` ")
    print("")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)s %(levelname)s %(message)s',
                        handlers=[
                            logging.FileHandler(LOGNAME),
                            logging.StreamHandler(sys.stdout)
                        ])
    print_smart_bedkow()
    get_input_parameters()

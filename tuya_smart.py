import logging
import sys
import tinytuya

LOGNAME = "smartbedkow.log"


class TuyaSmart:
    def __init__(self, name, id, ip_address, local_key):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)s %(levelname)s %(message)s',
                            handlers=[
                                logging.FileHandler(LOGNAME),
                                logging.StreamHandler(sys.stdout)
                            ])

        logging.info("Initializing LocalTuya device: %s..." % name)

        self.radiator = tinytuya.OutletDevice(id, ip_address, local_key)
        self.radiator.set_version(3.3)
        self.name = name
        self.on = False
        self.initialized = False

        status = self.get_status()

        if status:
            try:
                status_err = status["Error"]
            except KeyError:
                status_err = ""

            if status_err:
                logging.warning("Initialization of LocalTuya device %s failed. Error when getting the status: %s" %
                                (name, status_err))
            else:
                self.initialized = True
                logging.info("Initialized LocalTuya device: %s" % name)

        else:
            logging.warning("Initialization of LocalTuya device %s failed" % name)

    def turn_on(self):
        tinytuya.Device.turn_on(self.radiator)
        status_on = self.get_status()["dps"]["1"]
        self.on = status_on
        logging.info("Turned ON LocalTuya device: %s" % self.name)

    def turn_off(self):
        tinytuya.Device.turn_off(self.radiator)
        status_on = self.get_status()["dps"]["1"]
        self.on = status_on
        logging.info("Turned OFF LocalTuya device: %s" % self.name)

    def get_status(self):
        try:
            return tinytuya.OutletDevice.status(self.radiator)
        except ValueError:
            logging.warning("Could not get the status of %s" % self.name)

    def is_on(self):
        status_on = self.get_status()["dps"]["1"]
        self.on = status_on
        return status_on

    def get_current_temperature(self):
        current_temperature = self.get_status()["dps"]["4"]
        return current_temperature

    def get_set_temperature(self):
        set_temperature = self.get_status()["dps"]["3"]
        return set_temperature

    def get_heating_power(self):
        heating_power = self.get_status()["dps"]["7"]
        return heating_power

    def is_initialized(self):
        return self.initialized

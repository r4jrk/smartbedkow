import logging
import sys
import tinytuya

LOGNAME = "smartbedkow.log"


class TuyaSmart:

    def __init__(self, name, device_id, ip_address, local_key):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)s %(levelname)s %(message)s',
                            handlers=[
                                logging.FileHandler(LOGNAME),
                                logging.StreamHandler(sys.stdout)
                            ])

        logging.info("Initializing LocalTuya device: %s..." % name)

        self.radiator = tinytuya.OutletDevice(device_id, ip_address, local_key)
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
                logging.info("Initialization of LocalTuya device %s failed. Error when getting the status: %s" % (name, status_err))
            else:
                self.initialized = True
                logging.info("Initialized LocalTuya device: %s" % name)

        else:
            logging.info("Initialization of LocalTuya device %s failed" % name)


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
            logging.info("Could not get the status of %s" % self.name)

    def is_on(self):
        status_on = self.get_status()["dps"]["1"]
        self.on = status_on
        return status_on

    def is_initialized(self):
        return self.initialized

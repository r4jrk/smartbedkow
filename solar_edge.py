import datetime
import logging
import sys
import requests


LOGNAME = "smartbedkow.log"


class SolarEdge:

    def __init__(self, api_key, start_time, end_time):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s %(name)s %(levelname)s %(message)s',
                            handlers=[
                                logging.FileHandler(LOGNAME),
                                logging.StreamHandler(sys.stdout)
                            ])

        logging.info("Initializing SolarEdge API Connector...")

        self.API_KEY = api_key
        self.start_time = start_time
        self.end_time = end_time
        self.power_production = 0
        self.response_start_time = ''
        self.response_end_time = ''

        logging.info("SolarEdge API Connector initialized")

    def update_times(self, time_interval):
        self.start_time = datetime.datetime.now() - datetime.timedelta(minutes=time_interval)
        self.end_time = datetime.datetime.now()

        logging.info("SolarEdge API request start_time updated to: " + self.start_time.strftime("%Y-%m-%d %H:%M:%S"))
        logging.info("SolarEdge API request end_time updated to: " + self.end_time.strftime("%Y-%m-%d %H:%M:%S"))

    def get_power_production(self):
        return self.power_production

    def get_response_start_time(self):
        return self.response_start_time

    def get_response_end_time(self):
        return self.response_end_time

    def get_api_call_api_key(self):
        return "?api_key=" + self.API_KEY

    def get_api_call_star_time(self):
        return "&startTime=" + self.start_time.strftime("%Y-%m-%d %H:%M:%S")

    def get_api_call_end_time(self):
        return "&endTime=" + self.end_time.strftime("%Y-%m-%d %H:%M:%S")

    def build_solar_edge_api_uri(self):
        api_key = self.get_api_call_api_key()
        start_time = self.get_api_call_star_time()
        end_time = self.get_api_call_end_time()
        api_connection_url = "https://monitoringapi.solaredge.com/site/2431166/powerDetails" \
                             + api_key + start_time + end_time

        logging.info("SolarEdge API request URL: %s" % api_connection_url)

        return api_connection_url

    def get_solar_edge_api_response(self):
        logging.info("Building SolarEdge API request...")
        uri = self.build_solar_edge_api_uri()

        logging.info("Sending request to SolarEdge API...")
        request = requests.get(uri)

        logging.info("Response from SolarEdge API received")
        api_response = request.json()

        logging.info("Parsing SolarEdge API response...")

        try:
            wattage = api_response["powerDetails"]["meters"][0]["values"][1]["value"]
        except KeyError:
            try:
                wattage = api_response["powerDetails"]["meters"][0]["values"][0]["value"]
            except KeyError:
                wattage = 0

        response_start_time = api_response["powerDetails"]["meters"][0]["values"][0]["date"]
        response_end_time = api_response["powerDetails"]["meters"][0]["values"][1]["date"]

        logging.info("Response parsed. Production between %s and %s: %s W" % (response_start_time,
                     response_end_time, round(wattage, 2)))

        self.response_start_time = response_start_time
        self.response_end_time = response_end_time
        self.power_production = wattage

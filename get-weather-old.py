# Pull weather data from several stations managed by victoriaweather.ca and
# push the data into an InfluxDB database.

import requests
import xmltodict
from influxdb import client as influxdb

# Set up a list with weather station names.
stations = ["Sidney", "Kelset", "Keating"]

# Set up the base URL for the current weather.
base_url = "http://www.victoriaweather.ca/stations/"
base_resource = "/current.xml"

# Set up connection to InfluxDB database.
db = influxdb.InfluxDBClient('lurch.jvangorp.info', 8086, 'monitor', 'monitor', 'monitor')

# Get data from each station and push to InfluxDB.
for station in stations:
        current_summary_xml = requests.get(base_url + station + base_resource)
        current_summary = xmltodict.parse(current_summary_xml.text)

        # Parse XML payload from victoriaweather.ca for specific vars.
        temperature = float(current_summary['current_observation']['temperature'])
        humidity = float(current_summary['current_observation']['humidity'])
        pressure = float(current_summary['current_observation']['pressure'])
        insolation = float(current_summary['current_observation']['insolation'])
        wind_speed = float(current_summary['current_observation']['wind_speed'])
        wind_speed_heading = current_summary['current_observation']['wind_speed_heading']

        # Drop parsed weather vars into dict object expected by InfluxDB module.
        weather = {}
        weather['name'] = 'weather'
        weather['columns'] = ['station', 'temperature', 'humidity', 'pressure',
                'insolation', 'wind_speed', 'wind_speed_heading']
        weather['points'] = [[station, temperature, humidity, pressure, insolation,
                wind_speed, wind_speed_heading]]

        # Push data payload to InfluxDB.
        db.write_points_with_precision([weather], time_precision='s')

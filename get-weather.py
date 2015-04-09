# Pull weather data from several stations managed by victoriaweather.ca and
# push the data into the RabbitMQ queue.

import pika
import requests
import time

# Set up the base URL for the current weather.
base_url = "http://www.victoriaweather.ca/stations/"
base_resource = "/current.xml"

# Set up a list with weather station names.
stations = ['Sidney', 'Kelset', 'Keating', 'Brentwood', 'Butchart']

# Continually scan list of weather stations for new data.
while True:

	# Set up the RabbitMQ connection.
	connection = pika.BlockingConnection(pika.ConnectionParameters(
    	host='localhost'))
	channel = connection.channel()
	channel.exchange_declare(exchange='victoriaweather.ca',
                         type='fanout')

	# Get data from each station and push to InfluxDB.
	for station in stations:
	
		current_summary = requests.get(base_url + station + base_resource)

		if current_summary.status_code == 200:
			# Send station current weather update to the RabbitMQ queue.
			channel.basic_publish(exchange='victoriaweather.ca',
                    routing_key='',
                    body=current_summary.text)

	connection.close()

	# Wait a bit before the next scan of weather stations.
	time.sleep(300)
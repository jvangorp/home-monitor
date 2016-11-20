# Pull demand data from the Rainforest Automation cloud service and
# push the data into the RabbitMQ queue.

import pika
import requests
import time
from ConfigParser import SafeConfigParser

# Read in app config values.
config = SafeConfigParser()
config.read('monitor-apps-config.ini')
cloud_id = config.get('RainforestCloud', 'cloud_id')
user = config.get('RainforestCloud', 'user')
password = config.get('RainforestCloud', 'password')

# Switch off warnings in urllib3 (used by requests) to suppress warnings that
# arise from the use of an unverified (self-signed) SSL certificate.
requests.packages.urllib3.disable_warnings()

# Set up the base URL for the Rainforest Automation cloud.
url = "https://rainforestcloud.com:9445/cgi-bin/post_manager"

# Set up headers for the demand request POST
headers = {}
headers['Content-Type'] = 'text/xml'
headers['Cloud-ID'] = cloud_id
headers['User'] = user
headers['Password'] = password

# Set up demand request
body = """
<Command>
<Name>get_instantaneous_demand</Name>
</Command>"""

# Loop through demand measurement requests from the cloud service.
while True:

	# Set up the RabbitMQ connection.
	connection = pika.BlockingConnection(pika.ConnectionParameters(
    	host='localhost'))
	channel = connection.channel()
	channel.exchange_declare(exchange='vangorp.home.eagle',
                         type='fanout')

	# Get demand data and push to RabbitMQ queue.
	demand = requests.post(url, data=body, headers=headers)
	print demand.text

	if demand.status_code == 200:
		# Send station current weather update to the RabbitMQ queue.
		channel.basic_publish(exchange='vangorp.home.eagle',
                   routing_key='',
                   body=demand.text)

	connection.close()

	# Wait a bit before the next scan of weather stations.
	time.sleep(10)

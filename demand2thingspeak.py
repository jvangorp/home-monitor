# Receive demand values from the RabbitMQ queue and send to ThingSpeak.
import pika
from lxml import etree
import requests
from ConfigParser import SafeConfigParser

# Read in app config values.
config = SafeConfigParser()
config.read('monitor-apps-config.ini')
upload_url = config.get('ThingSpeak', 'upload_url')
API_key = config.get('ThingSpeak', 'API_key')

# Set up the connection to the RabbitMQ server.
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

# Set up the link to the selected RabbitMQ exchange.
channel.exchange_declare(exchange='vangorp.home.eagle',
                         type='fanout')

# Grab a queue name and bind it to the exchange.
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='vangorp.home.eagle',
                   queue=queue_name)

# Set up callback function to process queue messages.
def callback(ch, method, properties, body):
    # Parse the message into an XML document.
    message = etree.fromstring(body)

    # Extract timestamp and remove the 's' at the end.
    timestamp = message.attrib['timestamp']
    timestamp = timestamp[:-1]

    # Extract set of elements from Eagle gateway post.
    fragment = message[0]

    # Process the InstantaneousDemand fragment.
    if fragment.tag == 'InstantaneousDemand':

        # Extract demand measurement value.
        demand = int(fragment.findtext('Demand'), base=0)
        multiplier = int(fragment.findtext('Multiplier'), base=0)
        divisor = int(fragment.findtext('Divisor'), base=0)
        InstantaneousDemand = (demand * multiplier)/float(divisor)

        # Push data to ThingSpeak.
        payload = {'key': API_key, 'field1': InstantaneousDemand}
        response = requests.post(upload_url, params=payload)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()
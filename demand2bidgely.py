# Receive demand values from the RabbitMQ queue and send to Bidgely.
import pika
from lxml import etree
import requests
from ConfigParser import SafeConfigParser

# Read in app config values.
config = SafeConfigParser()
config.read('monitor-apps-config.ini')
upload_url = config.get('Bidgely', 'upload_url')
meter_ID = config.get('Bidgely', 'meter_ID')

# Set additional Bidgely parameters.
API_version = '1.0'
meter_type = '0' # Bidgely type for total consumption (no generation)
stream_unit = 'kW' # Bidgely unit for instantaneous demand
stream_ID = 'InstantaneousDemand'

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

        # Build the data payload as an XML document.
        doc = etree.Element('upload')
        doc.set('version', API_version)

        meters = etree.SubElement(doc, 'meters')
        meter = etree.SubElement(meters, 'meter')
        meter.set('id', meter_ID)
        meter.set('type', meter_type)

        streams = etree.SubElement(meter, 'streams')
        stream = etree.SubElement(streams, 'stream')
        stream.set('id', stream_ID)
        stream.set('unit', stream_unit)

        data = etree.SubElement(stream, 'data')
        data.set('time', timestamp)
        data.set('value', str(InstantaneousDemand))

        payload = etree.tostring(doc)

        # POST the payload to the Bidgely API URL.
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(upload_url, data=payload, headers=headers)

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

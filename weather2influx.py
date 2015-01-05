# Receive victoriaweather.ca data from the RabbitMQ queue and store in the InfluxDB database.
import pika
from lxml import etree
from influxdb import client as influxdb
from ConfigParser import SafeConfigParser

# Read in app config values.
config = SafeConfigParser()
config.read('monitor-apps-config.ini')
server = config.get('InfluxDB', 'server')
port = config.getint('InfluxDB', 'port')
database = config.get('InfluxDB', 'database')
user = config.get('InfluxDB', 'user')
password = config.get('InfluxDB', 'password')

# Set up the connection to the RabbitMQ server.
connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
channel = connection.channel()

# Set up the link to the selected RabbitMQ exchange.
channel.exchange_declare(exchange='victoriaweather.ca',
                         type='fanout')

# Grab a queue name and bind it to the exchange.
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='victoriaweather.ca',
                   queue=queue_name)

# Set up connection to InfluxDB database.
db = influxdb.InfluxDBClient(server, port, user, password, database)


# Set up callback function to process queue messages.
def callback(ch, method, properties, body):

    message = etree.fromstring(body)

    # Extract timestamp and remove the 's' at the end.
    timestamp = message.attrib['timestamp']
    timestamp = timestamp[:-1]

    # Extract set of elements from Eagle gateway post.
    fragment = message[0]

    # Process the CurrentSummationDelivered fragment.
    if fragment.tag == 'CurrentSummationDelivered':

        # Extract energy consumption value.
        energy = int(fragment.findtext('SummationDelivered'), base=0)
        multiplier = int(fragment.findtext('Multiplier'), base=0)
        divisor = int(fragment.findtext('Divisor'), base=0)
        CurrentSummationDelivered = (energy * multiplier)/float(divisor)





        # Organize demand measurement into InfluxDB dict format.
        influx = {}
        influx['name'] = 'vangorp.home.energy'
        influx['columns'] = ['time', 'energy']
        influx['points'] = [[float(timestamp), CurrentSummationDelivered]]

        # Insert data into InfluxDB database.
        db.write_points_with_precision([influx], time_precision='s')

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

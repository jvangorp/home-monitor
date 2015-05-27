# Receive Eagle gateway messages from the RabbitMQ queue and
# restart the web endpoint when there is a loss of comms from the gateway.
import pika
from lxml import etree
import logging
import time
from ConfigParser import SafeConfigParser

# Read in app config values.
config = SafeConfigParser()
config.read('monitor-apps-config.ini')
host = config.get('Postgres', 'host')
database = config.get('Postgres', 'database')
user = config.get('Postgres', 'user')
password = config.get('Postgres', 'password')

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

# Set up Python logging defaults
logging.basicConfig(filename='eagle-endpoint.log')
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Set up callback function to process queue messages.
def callback(ch, method, properties, body):
    # print " [x] %r" % (body,)
    message = etree.fromstring(body)

    # Extract timestamp and remove the 's' at the end.
    eagle_time = message.attrib['timestamp']
    eagle_time = int(eagle_time[:-1])

    # Compare Eagle gateway time with server time - if the difference
    # is too large, restart the 'eagle-endpoint.py' script and
    # log an error.
    server_time = int(time.time())
    print(abs(server_time - eagle_time))



channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

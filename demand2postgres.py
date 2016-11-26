# Receive demand values from the RabbitMQ queue and store in
# the Postgres database.
import pika
from lxml import etree
import psycopg2
from ConfigParser import SafeConfigParser

# Read in app config values.
config = SafeConfigParser()
config.read('monitor-apps-config.ini')
host = config.get('Postgres', 'host')
database = config.get('Postgres', 'database')
user = config.get('Postgres', 'user')
password = config.get('Postgres', 'password')

# Offset between Unix Epoch time and the UTC time format
# used by the Eagle gateway (seconds since Jan 1, 2000).
ts_offset = 946684800

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

# Set up connection to Postgres database.
conn_string = """
host={0} dbname={1} user={2} password={3}
""".format(host, database, user, password)

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()


# Set up callback function to process queue messages.
def callback(ch, method, properties, body):
    # print " [x] %r" % (body,)
    message = etree.fromstring(body)

    # Process the InstantaneousDemand fragment.
    if message.tag == 'InstantaneousDemand':

        # Extract demand measurement value.
        timestamp = int(message.findtext('TimeStamp'), base=0)
        demand = int(message.findtext('Demand'), base=0)
        multiplier = int(message.findtext('Multiplier'), base=0)
        divisor = int(message.findtext('Divisor'), base=0)
        InstantaneousDemand = (demand * multiplier)/float(divisor)

        # Create INSERT statement.
        SQL = """insert into demand (ts, kw)
            values (to_timestamp(%s), %s) on conflict do nothing;"""

        # Insert data into Postgres database but just skip this insert
        # if an error is thrown - this could happen if sequential demand 
        # measurements have the same timestamp.
        try:
            cursor.execute(SQL, (timestamp + ts_offset, InstantaneousDemand))
            print cursor.query
            print cursor.statusmessage
    
        except psycopg2.IntegrityError:
            conn.rollback()
    
        else:
            conn.commit()

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

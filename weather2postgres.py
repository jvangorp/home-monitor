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

# Set up connection to Postgres database.
conn_string = """
host={0} dbname={1} user={2} password={3}
""".format(host, database, user, password)

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# Set up callback function to process queue messages.
def callback(ch, method, properties, body):
    message = etree.fromstring(body)

    # Get the weather station name.
    station = message.findtext('station_name')

    # Get the timestamp and format it for Postgres.
    timestamp = message.findtext('observation_time')
    timestamp = timestamp.replace(',', '') # remove comma in timestamp

    # Extract measurement values from message.
    temperature = message.findtext('temperature')
    humidity = message.findtext('humidity')
    pressure = message.findtext('pressure')
    insolation = message.findtext('insolation')
    rain = message.findtext('rain')
    wind_speed = message.findtext('wind_speed')
    wind_speed_heading = message.findtext('wind_speed_heading')

    # Create INSERT statement.
    SQL = """
    insert into weather (ts, station, temperature, humidity, 
        pressure, insolation, rain, wind_speed, wind_speed_heading)
    values (to_timestamp(%s, 'YYYY/MM/DD hh24:mi'), %s,
         %s, %s, %s, %s, %s, %s, %s) on conflict do nothing;
    """

    # Insert data into Postgres database but just continue if an error 
    # is thrown.
    try:
        cursor.execute(SQL, (timestamp, station, temperature, humidity, 
            pressure, insolation, rain, wind_speed, wind_speed_heading))

    except psycopg2.IntegrityError:
        conn.rollback()

    else:
        conn.commit()

channel.basic_consume(callback,
                      queue=queue_name,
                      no_ack=True)

channel.start_consuming()

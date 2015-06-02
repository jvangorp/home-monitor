# Get the latest kW demand record from the Postgres database and
# restart the web endpoint if the timestamp is too old.
import logging
import time
import psycopg2
from ConfigParser import SafeConfigParser

# Read in app config values.
config = SafeConfigParser()
config.read('monitor-apps-config.ini')
host = config.get('Postgres', 'host')
database = config.get('Postgres', 'database')
user = config.get('Postgres', 'user')
password = config.get('Postgres', 'password')

# Set up Python logging defaults
logging.basicConfig(filename='eagle-watchdog.log')
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Set up connection to Postgres database.
conn_string = """
host={0} dbname={1} user={2} password={3}
""".format(host, database, user, password)

conn = psycopg2.connect(conn_string)
cursor = conn.cursor()

# Get the latest kW demand timestamp (in epoch form) from Postgres.
query = "select extract(epoch from ts) from demand order by ts desc limit 1;"
cursor.execute(query)
latest_timestamp = cursor.fetchone()

# Compare latest kW demand timestamp against current time.
# time_delta = abs()


# Flask web application that receives datab from the Rainforest Automation
# Eagle gateway and pushes the XML fragments to the RabbitMQ queue.

from flask import Flask, request, Response
import pika

app = Flask(__name__)

@app.route('/eagle', methods=['POST'])
def eagle_endpoint():

    # Set up the RabbitMQ connection.
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host='localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='vangorp.home.eagle',
                         type='fanout')

    # Send payload to the selected RabbitMQ exchange.
    channel.basic_publish(exchange='vangorp.home.eagle',
                      routing_key='',
                      body=request.data)

    connection.close()

    return Response(status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug='False')
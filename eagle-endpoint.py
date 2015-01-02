# Flask web application that receives data from the Rainforest Automation
# Eagle gateway and pushes the XML fragments to a RabbitMQ queue.

from flask import Flask, request, Response
import pika
from lxml import etree

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

    # Parse payload from Eagle gateway and look for
    # FastPollStatus messages.
    message = etree.fromstring(request.data)
    fragment = message[0]

    if fragment.tag == 'FastPollStatus':
      frequency = int(fragment.findtext('Frequency'), base=0)
      mac_id = fragment.findtext('DeviceMacId')

      # If fast polling is disabled, set it to 5s for 15 min and
      # build set_fast_poll response to send to the gateway.
      if frequency == 0:
        
        command = etree.Element('RavenCommand')
        name_element = etree.SubElement(command, 'Name')
        mac_element = etree.SubElement(command, 'MacId')
        freq_element = etree.SubElement(command, 'Frequency')
        dur_element = etree.SubElement(command, 'Duration')

        name_element.text = 'set_fast_poll'
        mac_element.text = mac_id
        freq_element.text = '0x05'
        dur_element.text = '0x0F'

        response = etree.tostring(command)
        return response

      else:
        return Response(status=200)

    else:
      return Response(status=200)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug='False')
monitor-apps
============

This repository contains a collection of small scripts that form a monitoring system using a publish/subscribe pattern. This approach is used to receive data streamed by an [Eagle gateway](http://rainforestautomation.com/rfa-z109-eagle/) (built by [Rainforest Automation](http://rainforestautomation.com)) and push the data into a message queue for consumption by separate scripts.

**Figure 1** shows how the components of this monitoring system fit together. The Eagle gateway polls (via [ZigBee](http://www.zigbee.org) link) the BC Hydro meter monitoring my home electrical service and pushes XML snippets containing data via HTTP POST. The [eagle-endpoint.py](https://github.com/jvangorp/monitor-apps/blob/master/eagle-endpoint.py) script (built with [Flask](http://flask.pocoo.org)) receives the XML snippets and pushes them into a [RabbitMQ](http://www.rabbitmq.com) publish/subscribe queue. Other Python scripts (such as [demand2bidgely.py](https://github.com/jvangorp/monitor-apps/blob/master/demand2bidgely.py)) receive the XML snippets from the queue, parse out data of interest and push that data into other services (such as [Bidgely](https://www.bidgely.com), [dweet](http://dweet.io) and [EmonCMS](http://emoncms.org)). Check out the links below for two services that make power data from my home publicly available:

- [dweet.io feed](http://dweet.io/follow/vangorp-home)
- [ThingSpeak feed](https://thingspeak.com/channels/22462#publicview)


![Figure 1: Monitoring system](https://raw.githubusercontent.com/jvangorp/monitor-apps/master/images/fig1-monitoring-system.png "Figure 1")

**Figure 1**: Monitoring system components.


An overview of the publish/subscribe structure set up with RabbitMQ is shown in **Figure 2**. A _producer_ application publishes messages to an _exchange_ which feeds all received messages into multiple _queues_ (one for each _consumer_). RabbitMQ provides a simple mechanism for new consumers to subscribe to an exchange, passing back the name of the queue for that consumer to use. 

The Python implementation used here closely follows the [Python publish/subscribe tutorial](http://www.rabbitmq.com/tutorials/tutorial-three-python.html) posted on the RabbitMQ web site. 

![Figure 2: Publish/subscribe exchange with queues](https://raw.githubusercontent.com/jvangorp/monitor-apps/master/images/fig2-publish-subscribe.png "Figure 2")

**Figure 2**: Publish/subscribe message queue.



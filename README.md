monitor-apps
============

This repository contains a collection of small apps that form a monitoring system using a publish/subscribe pattern. This approach is used to receive data streamed by an Eagle gateway (built by Rainforest Automation) and push the data into a message queue for consumption by separate apps.

**Figure 1** shows how the components of this monitoring system fit together. The Eagle gateway polls (via [ZigBee](http://www.zigbee.org) link) the BC Hydro meter monitoring my home electrical service and pushes XML snippets containing data via HTTP POST. A small web application (built with [Flask](http://flask.pocoo.org)) receives the XML snippets and pushes them into a [RabbitMQ](http://www.rabbitmq.com) publish/subscribe queue. A variety of small Python apps receive the XML snippets from the queue, parse out data of interest and push that data into other services (such as [Bidgely](https://www.bidgely.com), [dweet](http://dweet.io) and [EmonCMS](http://emoncms.org)). Check out the links below for two services that make power data from my home publicly available:

- [dweet.io feed](http://dweet.io/follow/vangorp-home)
- [ThingSpeak feed](https://thingspeak.com/channels/22462#publicview)


![Figure 1: Monitoring system](https://raw.githubusercontent.com/jvangorp/monitor-apps/master/images/fig1-monitoring-system.png "Figure 1")

Some more text, and another image.

![Figure 2: Publish/subscribe exchange with queues](https://raw.githubusercontent.com/jvangorp/monitor-apps/master/images/fig2-publish-subscribe.png "Figure 2")



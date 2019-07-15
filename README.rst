################
pyApp - aio-pika
################

*Let us handle the boring stuff!*

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
      :alt: Once you go Black...

This extension provides a *client* factory for
`aio-pika <https://github.com/mosquito/aio-pika>`_ to allow connection parameters
to be configured in a pyApp settings file. The extension also provides
`pyApp Messaging <http://github.com/pyapp-org/pyapp-messaging/>`_ implementations
of Message and Pub/Sub queue types.

The extension also provides checks to confirm the settings are correct.


Installation
============

Install using *pip*::

    pip install pyapp-aio-pika

Install using *pipenv*::

    pipenv install pyapp-aio-pika


Usage
=====


API
===

Messaging Interface
-------------------

The is the abstract interface defined by *pyApp Messaging*. Unless your application
has very specific needs this is likely the best option.

To use the messaging interface use the factories defined by
`pyApp Messaging <http://github.com/pyapp-org/pyapp-messaging/>`_.

Both AsyncIO Message and Pub/Sub queue types are supported.

`pyapp_ext.messaging.asyncio.DirectSender`

    Message sender, uses a direct exchange.

`pyapp_ext.messaging.asyncio.FanOutReceiver`

    Pub/Sub queue publisher, uses fan-out exchange.

`pyapp_ext.messaging.asyncio.Receiver`

    Message receiver, uses a persistent queue linked to an exchange.

`pyapp_ext.messaging.asyncio.FanOutReceiver`

    Pub/Sub queue subscriber, uses a exclusive queue linked to an exchange.


Low Level
---------

`pyapp_ext.aio_pika.get_robust_connection(name: str = None) -> Connection`
   
      Get a "robust" connection from AIO Pika
      
`pyapp_ext.aio_pika.get_connection(name: str = None) -> Connection`
 
      Get a connection from AIO Pika

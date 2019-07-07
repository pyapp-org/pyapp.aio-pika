# from pickle import dumps as serialise, loads as deserialise
import asyncio
from json import dumps as serialise, loads as deserialise

from aio_pika import Channel, Connection, Exchange, Message, IncomingMessage
from typing import Sequence, Optional, Dict, Any
from pyapp_ext.messaging.asyncio import bases

from .factory import get_robust_connection

__all__ = ("MessageSender", "MessageReceiver", "MessagePublisher", "MessageSubscriber")


class MessageBase:
    """
    Base Message Queue
    """

    __slots__ = ("channel_number", "amqp_config", "_connection", "_channel")

    def __init__(self, amqp_config: str = None, channel_number: int = None):
        self.amqp_config = amqp_config
        self.channel_number = channel_number

        self._connection: Optional[Connection] = None
        self._channel: Optional[Channel] = None

    async def open(self):
        """
        Open queue
        """
        self._connection = await get_robust_connection(self.amqp_config)
        self._channel = await self._connection.channel(self.channel_number)

    async def close(self):
        """
        Close Queue
        """
        if self._channel:
            await self._channel.close()
            self._channel = None
        if self._connection:
            await self._connection.close()
            self._connection = None


class MessageSender(MessageBase, bases.MessageSender):
    """
    AIO Pika based message sender
    """

    __slots__ = ("routing_key",)

    def __init__(
        self, *, routing_key: str, amqp_config: str = None, channel_number: int = None
    ):
        super().__init__(amqp_config, channel_number)
        self.routing_key = routing_key

    async def send(self, kwargs: Dict[str, Any]):
        await self._channel.default_exchange.publish(
            Message(body=serialise(kwargs), content_type="application/json"),
            routing_key=self.routing_key,
        )


class MessageReceiver(MessageBase, bases.MessageReceiver):
    """
    AIO Pika based message receiver
    """

    __slots__ = ("queue_name", "prefetch_count")

    def __init__(self, *, queue_name: str, prefetch_count: int = 1, amqp_config: str = None, channel_number: int = None):
        super().__init__(amqp_config, channel_number)
        self.queue_name = queue_name
        self.prefetch_count = prefetch_count

    async def open(self):
        await super().open()
        await self._channel.set_qos(prefetch_count=self.prefetch_count)

    async def receive(self, message: IncomingMessage):
        async with message.process():
            print(message.body)
            await asyncio.sleep(1)

    async def listen(self):
        queue = await self._channel.declare_queue(self.queue_name)
        return queue.consume(self.receive)


class MessagePublisher(MessageBase, bases.MessagePublisher):
    """
    AIO Pika based message publisher
    """

    __slots__ = ()

    def __init__(self, *, amqp_config: str = None, channel_number: int = None):
        super().__init__(amqp_config, channel_number)

    async def publish(self, kwargs: Dict[str, Any]):
        pass


class MessageSubscriber(MessageBase, bases.MessageSubscriber):
    """
    AIO Pika based message subscriber
    """

    __slots__ = ()

    def __init__(self, *, amqp_config: str = None, channel_number: int = None):
        super().__init__(amqp_config, channel_number)

    async def subscribe(self, topic: str):
        pass

    async def cancel_subscription(self, topic: str):
        pass

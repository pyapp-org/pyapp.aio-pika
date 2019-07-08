# from pickle import dumps as serialise, loads as deserialise
import asyncio
from json import dumps as serialise, loads as deserialise

from aio_pika import Channel, Connection, Exchange, Message, IncomingMessage, ExchangeType
from typing import Sequence, Optional, Dict, Any

from pyapp_ext.messaging.asyncio import bases

from .factory import get_robust_connection

__all__ = ("MessageSender", "MessageReceiver", "MessagePublisher", "MessageSubscriber")


class MessageBase:
    """
    Base Message Queue
    """

    __slots__ = (
        "amqp_config",
        "channel_number",
        "_connection",
        "_channel",
    )

    def __init__(
        self,
        amqp_config: str = None,
        channel_number: int = None,
    ):
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
    AIO Pika based message sender/publisher.

    With AMQP senders and publishers are the same.

    """

    __slots__ = ("routing_key", "exchange_name")

    def __init__(
        self,
        *,
        routing_key: str,
        amqp_config: str = None,
        channel_number: int = None,
        exchange_name: str = None
    ):
        super().__init__(amqp_config, channel_number)
        self.routing_key = routing_key
        self.exchange_name = exchange_name

    async def exchange(self) -> Exchange:
        """
        Declare exchange instance.
        """
        if self.exchange_name:
            return await self._channel.declare_exchange(
                self.exchange_name,
                type=ExchangeType.DIRECT,
                durable=True
            )
        else:
            return self._channel.default_exchange

    async def publish_raw(self, body: bytes, *, content_type: str = None):
        """
        Publish a raw message (message is raw bytes)
        """
        exchange = await self.exchange()
        await exchange.publish(Message(body, content_type=content_type), self.routing_key)

    async def send(self, kwargs: Dict[str, Any]):
        """
        Send a message
        """
        await self.publish_raw(serialise(kwargs).encode(), content_type="application/json")


class MessageReceiver(MessageBase, bases.MessageReceiver):
    """
    AIO Pika based message receiver
    """

    __slots__ = ("queue_name", "prefetch_count")

    def __init__(
        self,
        *,
        queue_name: str,
        prefetch_count: int = 1,
        amqp_config: str = None,
        channel_number: int = None
    ):
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
        """
        Listen for messages.
        """
        queue = await self._channel.declare_queue(self.queue_name)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.receive(message)


class MessagePublisher(MessageBase, bases.MessagePublisher):
    """
    AIO Pika based message sender/publisher.

    With AMQP senders and publishers are the same.

    """

    __slots__ = ("routing_key", "exchange_name")

    def __init__(
        self,
        *,
        routing_key: str,
        amqp_config: str = None,
        channel_number: int = None,
        exchange_name: str = None
    ):
        super().__init__(amqp_config, channel_number)
        self.routing_key = routing_key
        self.exchange_name = exchange_name

    async def exchange(self) -> Exchange:
        """
        Declare exchange instance.
        """
        if self.exchange_name:
            return await self._channel.declare_exchange(
                self.exchange_name,
                type=ExchangeType.FANOUT,
                durable=False,
            )
        else:
            return self._channel.default_exchange

    async def publish_raw(self, body: bytes, *, content_type: str = None):
        """
        Publish a raw message (message is raw bytes)
        """
        exchange = await self.exchange()
        await exchange.publish(Message(body, content_type=content_type), self.routing_key)

    async def publish(self, kwargs: Dict[str, Any]):
        """
        Publish a message
        """
        await self.publish_raw(serialise(kwargs).encode(), content_type="application/json")


class MessageSubscriber(MessageBase, bases.MessageSubscriber):
    """
    AIO Pika based message subscriber
    """

    __slots__ = ("exchange_name", "prefetch_count")

    def __init__(
        self,
        *,
        exchange_name: str,
        prefetch_count: int = 1,
        amqp_config: str = None,
        channel_number: int = None
    ):
        super().__init__(amqp_config, channel_number)
        self.exchange_name = exchange_name
        self.prefetch_count = prefetch_count

    async def open(self):
        await super().open()
        await self._channel.set_qos(prefetch_count=self.prefetch_count)

    async def receive(self, message: IncomingMessage):
        async with message.process():
            print(message.body)
            await asyncio.sleep(1)

    async def subscribe(self, topic: str):
        queue = await self._channel.declare_queue(exclusive=True)
        await queue.bind(self.exchange_name)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                await self.receive(message)

    async def cancel_subscription(self, topic: str):
        pass

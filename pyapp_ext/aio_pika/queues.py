from aio_pika import Channel, Connection, Exchange, Message, ExchangeType
from typing import Optional, Union

from pyapp_ext.messaging.asyncio import bases

from .factory import get_robust_connection

__all__ = ("DirectSender", "FanOutSender", "Receiver", "FanOutReceiver")


class AMQPBase:
    """
    Base Message Queue
    """

    __slots__ = (
        "amqp_config",
        "channel_number",
        "routing_key",
        "_connection",
        "_channel",
    )

    def __init__(
        self, amqp_config: str = None, channel_number: int = None, routing_key: str = ""
    ):
        self.amqp_config = amqp_config
        self.channel_number = channel_number
        self.routing_key = routing_key

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


class AMQPPublish(AMQPBase):
    """
    AIO Pika based message sender/publisher.

    :param queue_name: Name of the exchange to subscribe to.
    :param routing_key: Optional routing key for more complex configurations
    :param amqp_config: Specific AMQP config setting name
    :param channel_number: Specify a specific channel number

    """

    __slots__ = ("queue_name", "_exchange")

    def __init__(
        self,
        *,
        queue_name: str,
        routing_key: str = "",
        amqp_config: str = None,
        channel_number: int = None,
    ):
        super().__init__(amqp_config, channel_number, routing_key)
        self.queue_name = queue_name

        self._exchange: Optional[Exchange] = None

    async def close(self):
        if self._exchange:
            self._exchange = None

        await super().close()

    async def send_raw(
        self,
        body: Union[str, bytes],
        *,
        content_type: str = None,
        content_encoding: str = None,
    ):
        """
        Publish a raw message (message is raw bytes)
        """
        if isinstance(body, str):
            body = body.encode()

        await self._exchange.publish(
            Message(body, content_type=content_type, content_encoding=content_encoding),
            self.routing_key,
        )

    publish_raw = send_raw


class DirectSender(AMQPPublish, bases.MessageSender):
    """
    AIO Pika based message sender.
    """

    __slots__ = ()

    async def open(self):
        await super().open()

        self._exchange = await self._channel.declare_exchange(
            self.queue_name, type=ExchangeType.DIRECT, durable=True
        )


class FanOutSender(AMQPPublish, bases.MessageSender):
    """
    AIO Pika based message sender/publisher.
    """

    __slots__ = ()

    async def open(self):
        await super().open()
        self._exchange = await self._channel.declare_exchange(
            self.queue_name, type=ExchangeType.FANOUT, durable=True
        )


class Receiver(AMQPBase, bases.MessageReceiver):
    """
    AIO Pika based message receiver

    :param queue_name: Name of the exchange to subscribe to.
    :param routing_key: Optional routing key for more complex routing.
    :param prefetch_count: Number of messages to fetch at a time.
    :param amqp_config: Specific AMQP config setting name
    :param channel_number: Specify a specific channel number

    """

    __slots__ = ("queue_name", "prefetch_count")

    def __init__(
        self,
        *,
        queue_name: str,
        routing_key: str = "",
        prefetch_count: int = 1,
        amqp_config: str = None,
        channel_number: int = None,
    ):
        super().__init__(amqp_config, channel_number, routing_key)
        self.queue_name = queue_name
        self.prefetch_count = prefetch_count

    async def open(self):
        await super().open()
        await self._channel.set_qos(prefetch_count=self.prefetch_count)

    async def queue(self):
        return await self._channel.declare_queue(self.queue_name)

    async def listen(self):
        """
        Listen for messages.
        """
        queue = await self.queue()
        await queue.bind(self.queue_name, self.routing_key)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    await self.receive(
                        message.body, message.content_type, message.content_encoding
                    )


class FanOutReceiver(Receiver):
    """
    AIO Pika based message receiver that creates a temporary listening queue
    """

    __slots__ = ()

    async def queue(self):
        return await self._channel.declare_queue(exclusive=True)

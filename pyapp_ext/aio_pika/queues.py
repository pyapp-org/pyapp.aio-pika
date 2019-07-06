# from pickle import dumps as serialise, loads as deserialise
from json import dumps as serialise, loads as deserialise

from aio_pika import Channel, Connection, Message
from typing import Sequence, Optional, Dict
from pyapp_ext.messaging import bases

from .factory import get_robust_connection

__all__ = ("MessageQueue",)


class MessageQueue(bases.AsyncMessageQueue):
    """
    Pika based message queue
    """

    __slots__ = (
        "routing_key",
        "channel_number",
        "exchange_name",
        "amqp_config",
        "_connection",
        "_channel",
    )

    def __init__(
        self,
        *,
        routing_key: str,
        channel_number: int = None,
        exchange_name: str = None,
        amqp_config: str = None
    ):
        self.routing_key = routing_key
        self.channel_number = channel_number
        self.exchange_name = exchange_name
        self.amqp_config = amqp_config

        self._connection: Optional[Connection] = None
        self._channel: Optional[Channel] = None

    @property
    def exchange(self):
        return self._channel.default_exchange

    async def open(self):
        self._connection = await get_robust_connection(self.amqp_config)
        self._channel = await self._connection.channel(self.channel_number)

    async def close(self):
        if self._channel:
            await self._channel.close()
            self._channel = None
        if self._connection:
            await self._connection.close()
            self._connection = None

    async def send(self, kwargs: Dict[str, str]):
        message = Message(
            body=serialise(kwargs),
            content_type="application/python-pickle",

        )
        await self.exchange.publish(message, self._channel, mandatory=True)

    async def receive(self, count: int = 1) -> Sequence[str]:
        pass

    async def listen(self):
        pass

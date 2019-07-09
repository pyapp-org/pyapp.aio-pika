from functools import partial
from pyapp.conf.helpers import ThreadLocalNamedSingletonFactory

from aio_pika import connect_robust, Connection

__all__ = (
    "Connection",
    "get_connection",
    "get_robust_connection",
    "connection_factory",
)


class ConnectionFactory(ThreadLocalNamedSingletonFactory[Connection]):
    """
    Factory for creating Connection.
    """

    defaults = {"host": "localhost", "port": 5672, "virtualhost": "/"}
    optional_keys = {"url", "login", "password", "ssl", "ssl_options"}

    async def create(self, name: str = None, robust: bool = True) -> Connection:
        config = self.get(name)
        return await connect_robust(**config)


connection_factory = ConnectionFactory("AMQP")
get_robust_connection = connection_factory.create
get_connection = partial(get_robust_connection, robust=False)

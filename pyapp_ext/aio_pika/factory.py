from functools import partial
from pyapp.conf.helpers import NamedFactory

from aio_pika import connect_robust, Connection

__all__ = ("Connection", "get_connection", "get_robust_connection", "connection_factory")


class ConnectionFactory(NamedFactory[Connection]):
    """
    Factory for creating Connection.
    """

    defaults = {
        "host": 'localhost',
        "port": 5672,
        "login": 'guest',
        "password": 'guest',
        "virtualhost": '/',
    }
    optional_keys = {
        "url",
        "ssl",
        "ssl_options"
    }

    async def create(self, name: str = None, robust: bool = True) -> Connection:
        config = self.get(name)
        return await connect_robust(**config)


connection_factory = ConnectionFactory("AMQP")
get_robust_connection = connection_factory.create
get_connection = partial(get_robust_connection, robust=False)

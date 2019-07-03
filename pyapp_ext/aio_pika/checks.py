from pyapp.checks.registry import register

from .factory import connection_factory

register(connection_factory)

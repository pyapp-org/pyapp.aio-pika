AMQP = {"default": {}}
"""
Named sets of connection arguments for AIO-Pika AMQP connection.

Use either a URL or broken out connection eg::

    AMQP = {"default": {
        "url": "amqp://localhost:5672,
    }}

    # or

    AMQP = {"default": {
        "host": 'localhost',
        "port": 5672,
        "login": 'guest',
        "password": 'guest',
        "virtualhost": '/',
        "ssl": None,
        "ssl_options": None
    }}

"""

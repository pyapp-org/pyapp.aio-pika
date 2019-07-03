from pyapp.conf import settings

# Ensure settings are configured
settings.configure(["pyapp_ext.aio_pika.default_settings"])

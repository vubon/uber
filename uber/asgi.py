import os
from channels import asgi

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uber.settings')

channel_layer = asgi.get_channel_layer()

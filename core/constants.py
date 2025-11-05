import os
from logging import DEBUG, INFO

from django.conf import settings

BASE_DIR = settings.BASE_DIR
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DEBUG_MODE: bool = settings.DEBUG

DEFAULT_LOG_FILE = os.path.join(LOG_DIR, 'django', 'django.log')
DEFAULT_ROTATING_LOG_FILE = DEFAULT_LOG_FILE
DEFAULT_LOG_MODE = 4 if DEBUG_MODE else 1
DEFAULT_LOG_LEVEL = DEBUG if DEBUG_MODE else INFO

EMAIL_LOG_ROTATING_FILE = os.path.join(LOG_DIR, 'emails', 'emails.log')
MONGO_LOG_ROTATING_FILE = os.path.join(LOG_DIR, 'mongo', 'mongo.log')
SUBSCRIBER_LOG_ROTATING_FILE = os.path.join(
    LOG_DIR, 'subscriber', 'subscriber.log'
)

os.makedirs(os.path.dirname(DEFAULT_ROTATING_LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(EMAIL_LOG_ROTATING_FILE), exist_ok=True)
os.makedirs(os.path.dirname(MONGO_LOG_ROTATING_FILE), exist_ok=True)
os.makedirs(os.path.dirname(SUBSCRIBER_LOG_ROTATING_FILE), exist_ok=True)

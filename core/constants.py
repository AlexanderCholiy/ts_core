from logging import DEBUG, INFO
from pathlib import Path

from django.conf import settings

BASE_DIR: Path = settings.BASE_DIR
LOG_DIR = BASE_DIR / 'logs'
DEBUG_MODE: bool = settings.DEBUG

DEFAULT_LOG_FILE = LOG_DIR / 'django' / 'django.log'
DEFAULT_ROTATING_LOG_FILE = DEFAULT_LOG_FILE
DEFAULT_LOG_MODE = 4 if DEBUG_MODE else 1
DEFAULT_LOG_LEVEL = DEBUG if DEBUG_MODE else INFO

EMAIL_LOG_FILE = LOG_DIR / 'emails' / 'emails.log'
MONGO_LOG_FILE = LOG_DIR / 'mongo' / 'mongo.log'
SUBSCRIBER_LOG_FILE = LOG_DIR / 'subscriber' / 'subscriber.log'

import logging
import os
from logging.handlers import RotatingFileHandler

from django.conf import settings


class FileRotatingLogger:
    def __init__(
        self,
        log_dir: str,
        filename: str = 'app.log',
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 5,
        debug: bool = False
    ) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if debug else logging.INFO)
        self.logger.propagate = False

        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, filename)

        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
            ' - %(name)s - [%(pathname)s]'
        )
        console_formatter = logging.Formatter('[%(levelname)s] %(message)s')

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8',
        )
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        if debug:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

    def get_logger(self: 'FileRotatingLogger') -> logging.Logger:
        return self.logger


email_logger = FileRotatingLogger(
    os.path.join(settings.BASE_DIR, 'log'), 'email.log', debug=settings.DEBUG
).get_logger()

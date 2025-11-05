import logging
from logging.handlers import RotatingFileHandler
from typing import Union

from .constants import (
    DEFAULT_LOG_FILE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_MODE,
    DEFAULT_ROTATING_LOG_FILE,
    EMAIL_LOG_ROTATING_FILE,
    MONGO_LOG_ROTATING_FILE,
    SUBSCRIBER_LOG_ROTATING_FILE
)
from .exceptions import LoggerError


class LoggerFactory:
    """
    Универсальный фабричный класс для логгера.

    Режимы:
        0 - Только консоль
        1 - Только ротация
        2 - Только файл
        3 - Файл + консоль
        4 - Консоль + ротация
    """

    DEFAULT_FORMAT = (
        '%(asctime)s | %(levelname).1s | %(name)s | %(funcName)s | %(message)s'
    )
    DEFAULT_DATEFMT = '%H:%M:%S'

    def __init__(
        self,
        name: str = __name__,
        rotating_file: str = DEFAULT_ROTATING_LOG_FILE,
        log_file: str = DEFAULT_LOG_FILE,
        level: Union[int, None] = None,
        mode: Union[int, None] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 2,
        fmt: str = None,
        datefmt: str = None,
    ):
        level = level if level is not None else DEFAULT_LOG_LEVEL
        mode = mode if mode is not None else DEFAULT_LOG_MODE

        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        if self.logger.handlers:
            self.logger.handlers.clear()

        formatter = logging.Formatter(fmt or self.DEFAULT_FORMAT)
        console_formatter = logging.Formatter(
            fmt or self.DEFAULT_FORMAT, datefmt or self.DEFAULT_DATEFMT
        )

        if mode == 0:  # только консоль
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        elif mode == 1:  # только ротация
            handler = RotatingFileHandler(
                rotating_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        elif mode == 2:  # только файл
            handler = logging.FileHandler(log_file, 'a', 'utf-8')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        elif mode == 3:  # файл + консоль
            file_handler = logging.FileHandler(log_file, 'a', 'utf-8')
            file_handler.setFormatter(formatter)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

        elif mode == 4:  # ротация + консоль
            rotating_handler = RotatingFileHandler(
                rotating_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            rotating_handler.setFormatter(formatter)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(rotating_handler)
            self.logger.addHandler(console_handler)

        else:
            raise LoggerError('Неверный режим логгера (mode). Допустимо 0–4.')

    def get_logger(self) -> logging.Logger:
        return self.logger


email_logger = LoggerFactory(
    'email_logger', EMAIL_LOG_ROTATING_FILE
).get_logger()

mongo_logger = LoggerFactory(
    'mongo_logger', MONGO_LOG_ROTATING_FILE
).get_logger()

subscriber_logger = LoggerFactory(
    'subscriber_logger', SUBSCRIBER_LOG_ROTATING_FILE
).get_logger()

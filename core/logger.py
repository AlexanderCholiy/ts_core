import logging
from enum import IntEnum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Union

from django.conf import settings

from core.constants import (
    EMAIL_LOG_FILE,
    MONGO_LOG_FILE,
    SUBSCRIBER_LOG_FILE,
)
from core.exceptions import LoggerError


class LoggerMode(IntEnum):
    CONSOLE = 0
    ROTATING_FILE = 1
    FILE = 2
    FILE_AND_CONSOLE = 3
    ROTATING_FILE_AND_CONSOLE = 4


class LoggerFactory:
    """
    Фабрика для создания и настройки логгера.

    Режимы:
        CONSOLE - только консоль
        ROTATING_FILE - только ротация
        FILE - только файл
        FILE_AND_CONSOLE - файл + консоль
        ROTATING_FILE_AND_CONSOLE - ротация + консоль
    """

    DEFAULT_FORMAT = (
        '%(asctime)s | %(levelname).1s | '
        '%(name)s | %(funcName)s | %(message)s'
    )
    DEFAULT_DATEFMT = '%H:%M:%S'
    DEFAULT_LOG_MODE = (
        LoggerMode.ROTATING_FILE_AND_CONSOLE
        if settings.DEBUG else LoggerMode.ROTATING_FILE
    )
    DEFAULT_LOG_LEVEL = logging.DEBUG if settings.DEBUG else logging.INFO

    def __init__(
        self,
        log_file: Union[str, Path],
        name: str = __name__,
        level: int = DEFAULT_LOG_LEVEL,
        mode: LoggerMode = DEFAULT_LOG_MODE,
        max_bytes: int = 10 * 1024 * 1024,
        backup_count: int = 2,
        fmt: str = DEFAULT_FORMAT,
        datefmt: str = DEFAULT_DATEFMT,
    ):
        self.log_file = Path(log_file)
        self.level = level

        try:
            self.mode = LoggerMode(mode)
        except ValueError as exc:
            raise LoggerError(
                'Неверный режим логгера. '
                'Допустимые значения: 0–4.'
            ) from exc

        if max_bytes <= 0:
            raise LoggerError('max_bytes должен быть больше 0.')

        if backup_count < 0:
            raise LoggerError('backup_count не может быть отрицательным.')

        if level not in (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ):
            raise LoggerError(
                'Неверный уровень логирования. '
                'Допустимые значения: DEBUG, INFO, WARNING, ERROR, CRITICAL.'
            )

        self.max_bytes = max_bytes
        self.backup_count = backup_count

        self.formatter = logging.Formatter(fmt)

        self.console_formatter = logging.Formatter(fmt, datefmt)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        self.logger.propagate = False

        self._clear_handlers()
        self._configure()

    def _clear_handlers(self) -> None:
        """Закрывает и удаляет существующие handlers."""
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

    @staticmethod
    def _prepare_path(path: Path) -> None:
        """Создаёт директорию для лог-файла."""
        path.parent.mkdir(parents=True, exist_ok=True)

    def _create_console_handler(self) -> logging.Handler:
        handler = logging.StreamHandler()
        handler.setFormatter(self.console_formatter)

        return handler

    def _create_file_handler(self) -> logging.Handler:
        self._prepare_path(self.log_file)

        handler = logging.FileHandler(
            self.log_file,
            mode='a',
            encoding='utf-8',
        )
        handler.setFormatter(self.formatter)

        return handler

    def _create_rotating_handler(self) -> logging.Handler:
        self._prepare_path(self.log_file)

        handler = RotatingFileHandler(
            self.log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8',
        )
        handler.setFormatter(self.formatter)

        return handler

    def _configure(self) -> None:
        if self.mode == LoggerMode.CONSOLE:
            self.logger.addHandler(self._create_console_handler())

        elif self.mode == LoggerMode.ROTATING_FILE:
            self.logger.addHandler(self._create_rotating_handler())

        elif self.mode == LoggerMode.FILE:
            self.logger.addHandler(self._create_file_handler())

        elif self.mode == LoggerMode.FILE_AND_CONSOLE:
            self.logger.addHandler(self._create_file_handler())
            self.logger.addHandler(self._create_console_handler())

        elif self.mode == LoggerMode.ROTATING_FILE_AND_CONSOLE:
            self.logger.addHandler(self._create_rotating_handler())
            self.logger.addHandler(self._create_console_handler())

    def get_logger(self) -> logging.Logger:
        return self.logger


email_logger = LoggerFactory(EMAIL_LOG_FILE, 'email_logger').get_logger()

mongo_logger = LoggerFactory(MONGO_LOG_FILE, 'mongo_logger').get_logger()

subscriber_logger = (
    LoggerFactory(SUBSCRIBER_LOG_FILE, 'subscriber_logger').get_logger()
)

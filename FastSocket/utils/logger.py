"""
Thread-safe logging for FastSocket using Python's stdlib logging module.

Public API is intentionally kept identical to the original Logger class so
all existing callers work without modification.
"""

import logging
import sys


class Color:
    PURPLE    = '\033[95m'
    CYAN      = '\033[96m'
    DARKCYAN  = '\033[36m'
    BLUE      = '\033[94m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    RED       = '\033[91m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    END       = '\033[0m'


class _ColoredFormatter(logging.Formatter):
    _COLORS = {
        logging.ERROR:    Color.RED,
        logging.WARNING:  Color.YELLOW,
        logging.INFO:     Color.GREEN,
        logging.DEBUG:    Color.YELLOW,
        logging.CRITICAL: Color.RED + Color.BOLD,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self._COLORS.get(record.levelno, '')
        tag   = getattr(record, 'fs_tag', record.levelname)
        return f'{color}[{tag}]{Color.END}: {record.getMessage()}'


class _PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        tag = getattr(record, 'fs_tag', record.levelname)
        return f'[{tag}]: {record.getMessage()}'


def _build_logger() -> logging.Logger:
    log = logging.getLogger('fastsocket')
    if not log.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(_ColoredFormatter())
        log.addHandler(handler)
    log.setLevel(logging.DEBUG)
    log.propagate = False
    return log


_log = _build_logger()


class Logger:
    @staticmethod
    def print_log_error(log, instance: str = 'FastSocket') -> None:
        _log.error(log, extra={'fs_tag': instance})

    @staticmethod
    def print_log_normal(log, instance: str = 'FastSocket') -> None:
        _log.info(log, extra={'fs_tag': instance})

    @staticmethod
    def print_log_debug(log) -> None:
        _log.debug(log, extra={'fs_tag': 'DEBUG'})

    @staticmethod
    def set_level(level: int) -> None:
        """Set the log level (e.g. logging.WARNING to silence debug/info)."""
        _log.setLevel(level)

    @staticmethod
    def add_file_handler(path: str) -> None:
        """Write log output to a file (plain text, no ANSI codes)."""
        fh = logging.FileHandler(path, encoding='utf-8')
        fh.setFormatter(_PlainFormatter())
        _log.addHandler(fh)

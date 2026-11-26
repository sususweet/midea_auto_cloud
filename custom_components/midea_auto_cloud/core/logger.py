import logging
import sys
from enum import IntEnum


class MideaLogType(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARN = logging.WARNING
    ERROR = logging.ERROR


class MideaLogger:
    @staticmethod
    def _log(log_type, log, device_id):
        # Resolve caller module with a single frame; avoid inspect.stack().
        try:
            module_name = sys._getframe(2).f_globals.get("__name__", __name__)
        except ValueError:
            module_name = __name__
        logger = logging.getLogger(module_name)
        if not logger.isEnabledFor(log_type):
            return
        if device_id is not None:
            log = f"[{device_id}] {log}"
        # stacklevel: _log -> debug/info/... -> real caller
        logger.log(log_type, log, stacklevel=3)

    @staticmethod
    def debug(log, device_id=None):
        MideaLogger._log(MideaLogType.DEBUG, log, device_id)

    @staticmethod
    def info(log, device_id=None):
        MideaLogger._log(MideaLogType.INFO, log, device_id)

    @staticmethod
    def warning(log, device_id=None):
        MideaLogger._log(MideaLogType.WARN, log, device_id)

    @staticmethod
    def error(log, device_id=None):
        MideaLogger._log(MideaLogType.ERROR, log, device_id)

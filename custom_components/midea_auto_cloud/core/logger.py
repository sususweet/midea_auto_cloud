import inspect
import logging
from enum import IntEnum


class MideaLogType(IntEnum):
    DEBUG = 1
    WARN = 2
    ERROR = 3


class MideaLogger:
    @staticmethod
    def _log(log_type, log, device_id):
        frm = inspect.stack()[2]
        mod = inspect.getmodule(frm[0])
        if device_id is not None:
            log = f"[{device_id}] {log}"
        if log_type == MideaLogType.DEBUG:
            logging.getLogger(mod.__name__).debug(log)
        elif log_type == MideaLogType.WARN:
            logging.getLogger(mod.__name__).warning(log)
        elif log_type == MideaLogType.ERROR:
            logging.getLogger(mod.__name__).error(log)

    @staticmethod
    def debug(log, device_id=None):
        MideaLogger._log(MideaLogType.DEBUG, log, device_id)

    @staticmethod
    def warning(log, device_id=None):
        MideaLogger._log(MideaLogType.WARN, log, device_id)

    @staticmethod
    def error(log, device_id=None):
        MideaLogger._log(MideaLogType.ERROR, log, device_id)
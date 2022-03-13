import logging
import sys

from Qt import QtCore


class Logger(QtCore.QObject):

    log_to_signal = QtCore.Signal(str, int)

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.log_to_signal.connect(self.on_log_to_signaled)

    @property
    def file_log(self) -> logging.FileHandler:
        if not hasattr(self, "_file_log"):
            self._file_log = logging.FileHandler(f"{self.log.name}.log")

        return self._file_log

    @property
    def log(self) -> logging.Logger:
        if not hasattr(self, "_log"):
            self._log = logging.getLogger(self.name)
            self._log.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            debug_handler = logging.StreamHandler(sys.stdout)
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(formatter)
            self._log.addHandler(debug_handler)

        return self._log

    def log_to(self, message: str, level: int = logging.DEBUG):
        self.log_to_signal.emit(message, level)

    @QtCore.Slot(str, int)
    def on_log_to_signaled(self, message: str, level: int):
        log_to_use = {
            logging.CRITICAL: self.log.critical,
            logging.ERROR: self.log.error,
            logging.WARNING: self.log.warning,
            logging.INFO: self.log.info,
            logging.DEBUG: self.log.debug,
        }[level]
        log_to_use(message)

    def set_level(self, level: int):
        self.log.setLevel(level)

    def enable_file_log(self, level: int):
        self.file_log.setLevel(level)
        self.log.addHandler(self.file_log)

    def disable_file_log(self):
        self.log.removeHandler(self.file_log)


def get_logger(name: str):
    return Logger(name)
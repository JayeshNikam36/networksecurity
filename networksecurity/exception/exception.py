import sys
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    """Base class for exceptions in the Network Security module."""

    def __init__(self, message):
        self.error_message = message
        _, _, exc_tb = sys.exc_info()

        if exc_tb is not None:
            self.lineno = exc_tb.tb_lineno
            self.file_name = exc_tb.tb_frame.f_code.co_filename
        else:
            self.lineno = None
            self.file_name = None

    def __str__(self):
        location = f"in file {self.file_name} at line {self.lineno}" if self.file_name and self.lineno else "at an unknown location"
        return f"Error occurred {location}: {self.error_message}"


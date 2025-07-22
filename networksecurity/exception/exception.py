import sys
import traceback
from networksecurity.logging import logger

class NetworkSecurityException(Exception):
    """Custom Exception class for Network Security errors."""

    def __init__(self, error: Exception, error_detail: sys):
        super().__init__(str(error))  # Initializes base Exception with error message
        self.error_message = self._get_detailed_error_message(error, error_detail)

    def _get_detailed_error_message(self, error: Exception, error_detail: sys) -> str:
        _, _, exc_tb = error_detail.exc_info()

        if exc_tb is not None:
            line_number = exc_tb.tb_lineno
            file_name = exc_tb.tb_frame.f_code.co_filename
            return f"Error occurred in file {file_name} at line {line_number}: {str(error)}"
        else:
            return f"Error: {str(error)} (location unknown)"

    def __str__(self):
        return self.error_message

import logging


class CustomFormatter(logging.Formatter):
    """Custom log formatter"""

    ERROR_FORMATTER = '[%(asctime)s] - [%(levelname)s] - [%(name)s] - ' \
                      '[%(filename)s():%(lineno)s - ' \
                      '%(funcName)5s()] [PID:%(process)d TID:%(thread)d] - ' \
                      '%(message)s'
    DEBUG_FORMATTER = '[%(asctime)s] - [%(levelname)s] - [%(name)s] - ' \
                      '[%(filename)s():%(lineno)s - %(funcName)5s()] - ' \
                      '%(message)s'
    INFO_FORMATTER = '[%(asctime)s] - [%(levelname)s] - [%(name)s] - ' \
                     '%(message)s'

    def __init__(self):
        super().__init__(fmt="%(levelno)d: %(msg)s",
                         datefmt='%d/%m/%Y %H:%M:%S',
                         style='%')

    def format(self, record):
        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_original = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno == logging.DEBUG:
            self._style._fmt = CustomFormatter.DEBUG_FORMATTER

        elif record.levelno == logging.INFO:
            self._style._fmt = CustomFormatter.INFO_FORMATTER

        elif record.levelno == logging.ERROR:
            self._style._fmt = CustomFormatter.ERROR_FORMATTER

        # Call the original formatter class to do the work
        result = logging.Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_original

        return result
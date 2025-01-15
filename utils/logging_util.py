import logging

class LoggerUtility:
    """
    Provides a utility class for setting up and configuring a logger.

    This class simplifies the process of configuring a logger with a
    specific name and log level. It ensures that there are no duplicated
    handlers for a logger of the same name and uses a standard log message
    format that includes the timestamp, logger name, logging level, and the
    message.

    :ivar logger: The configured logger instance.
    :type logger: logging.Logger
    """
    def __init__(self, logger_name: str, level=logging.INFO):
        self.logger = self._setup_logger(logger_name, level)

    @staticmethod
    def _setup_logger(name, level):
        """
        Sets up a logger with the specified name and log level. If the logger does not
        have any handlers applied, it creates a new stream handler with a predefined
        formatter and attaches it to the logger. The logger's logging level is then set
        to the provided level, ensuring that the logging configuration is consistent.

        The returned logger can be used to record log messages at the specified log
        level and can be further customized if needed.

        :param name: The name assigned to the logger instance.
        :type name: str
        :param level: The logging level to be set for the logger, typically one of the
            levels provided by the logging module, such as logging.DEBUG or logging.INFO.
        :type level: int
        :return: A configured logger instance with the provided name and level.
        :rtype: logging.Logger
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(level)
        return logger

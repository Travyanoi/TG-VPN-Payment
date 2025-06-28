import structlog
from telebot import ExceptionHandler

logger = structlog.get_logger("telebot")


class MyExceptionHandler(ExceptionHandler):
    def handle(self, exc):
        logger.exception(exc)

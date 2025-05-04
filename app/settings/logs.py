import logging

import structlog

DISABLED_LOGGERS = {
    'openai',
    'sentry_sdk',
    'celery.utils.functional',
    'git.cmd',
    'datadog',
}


def configure_logger(log_level: str = 'INFO', env_profile: str = 'Local') -> None:
    logging.basicConfig(level=log_level)

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt='iso', key='date'),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    structlog.configure(
        context_class=dict,
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=False,
    )

    for logger_name in DISABLED_LOGGERS:
        logging.getLogger(logger_name).setLevel(logging.ERROR)

import logging
import os
from typing import Any

from celery import Celery, signals, Task
import structlog

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

app = Celery(
    'workers-tasks',
    task_cls='apps.celery_app.TracedTask',
)

app.config_from_object('apps.celeryconfig')
app.autodiscover_tasks()

LOG_FORMATTER = {
    'json': structlog.stdlib.ProcessorFormatter(structlog.processors.JSONRenderer()),  # NOQA
    'console': structlog.stdlib.ProcessorFormatter(structlog.dev.ConsoleRenderer()),  # NOQA
}

formatter = LOG_FORMATTER[os.environ.get('LOG_FORMATTER', 'console')]


@signals.worker_ready.connect
def on_worker_ready(**kwargs: Any) -> None:
    import settings.urls  # noqa


@signals.after_setup_task_logger.connect
def after_setup_celery_task_logger(
        logger: logging.Logger,
        **kwargs: None,  # noqa
) -> None:
    """This function sets the 'celery.task' logger handler and formatter"""
    logger.handlers[0].setFormatter(formatter)


@signals.after_setup_logger.connect
def after_setup_celery_logger(
        logger: logging.Logger,
        **kwargs: None,  # noqa
) -> None:
    """This function sets the 'celery' logger handler and formatter"""
    logger.handlers[0].setFormatter(formatter)


logger = structlog.get_logger(__name__)


class TracedTask(Task):
    def __call__(self, *args: Any, **kwargs: dict[str, Any]) -> Any:
        with (
            structlog.contextvars.bound_contextvars(
                task_name=self.name,
                task_id=self.request.id,
            ),
        ):
            logger.info('task started', attempt=self.request.retries, task_id=self.request.id, task_name=self.name)
            try:
                result = super().__call__(*args, **kwargs)
            except Exception as exc:
                logger.exception(
                    'task failed',
                    attempt=self.request.retries,
                    exc=exc,
                )
                raise exc

            logger.info('task completed', attempt=self.request.retries, task_id=self.request.id, task_name=self.name)

            return result

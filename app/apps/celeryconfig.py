import os

from celery.schedules import crontab
from django.apps import apps
from django.db.models import Model
from kombu import Exchange, Queue
from kombu.utils.json import register_type

CELERY_BROKER_USER = os.environ.get('CELERY_BROKER_USER', 'Stels_Admin')
CELERY_BROKER_HOST = os.environ.get('CELERY_BROKER_HOST', 'rabbitmq')
CELERY_BROKER_PORT = os.environ.get('CELERY_BROKER_PORT', '5672')
CELERY_BROKER_PASSWORD = os.environ.get('CELERY_BROKER_PASSWORD', '237287')
CELERY_BROKER_VHOST = os.environ.get('CELERY_BROKER_VHOST', 'tg_vpn')

CELERY_BROKER_CONNECTION_STRING = '{schema}://{user}:{password}@{host}:{port}/{vhost}'.format(
    schema='amqp',
    user=CELERY_BROKER_USER,
    password=CELERY_BROKER_PASSWORD,
    host=CELERY_BROKER_HOST,
    port=CELERY_BROKER_PORT,
    vhost=CELERY_BROKER_VHOST,
)

broker_url = CELERY_BROKER_CONNECTION_STRING
broker_pool_limit = 10

task_serializer = 'json'

accept_content = ['json']
result_serializer = 'json'
enable_utc = True

QUEUE_DEFAULT = 'default'
QUEUE_FRANKFURT = 'frankfurt'
QUEUE_STOCKHOLM = 'stockholm'

task_default_queue = QUEUE_DEFAULT
task_queues = (
    Queue(QUEUE_DEFAULT, Exchange(QUEUE_DEFAULT), routing_key=QUEUE_DEFAULT),
    Queue(QUEUE_FRANKFURT, Exchange(QUEUE_FRANKFURT), routing_key=QUEUE_FRANKFURT),
    Queue(QUEUE_STOCKHOLM, Exchange(QUEUE_STOCKHOLM), routing_key=QUEUE_STOCKHOLM),
)

beat_schedule = {}

worker_max_tasks_per_child = int(os.getenv('WORKER_MAX_TASKS_PER_CHILD', 512))
worker_task_log_format = '[%(asctime)s] [%(levelname)s] %(name)s %(module)s %(process)d | %(message)s'  # noqa
worker_log_format = worker_task_log_format

broker_connection_retry_on_startup = False
broker_connection_retry = False

task_always_eager = bool(int(os.getenv('CELERY_ALWAYS_EAGER', False)))
task_store_eager_result = task_always_eager
deduplicate_successful_tasks = True

register_type(
    Model,
    "model",
    lambda o: [o._meta.label, o.pk],
    lambda o: apps.get_model(o[0]).objects.get(pk=o[1]),
)

import os
import socket
import struct
import sys
import threading
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gunicorn.arbiter import Arbiter
    from gunicorn.http import Request
    from gunicorn.http.wsgi import Response
    from apps.core.gunicorn_worker import ThreadWorkerWithMetrics


# Server settings
bind = '0.0.0.0:8000'
wsgi_app = "settings.wsgi:application"
keyfile = 'conf/ssl/certificate.key'
certfile = 'conf/ssl/certificate.crt'
ca_certs = 'conf/ssl/certificate_ca.crt'

# Worker processes
worker_class = 'apps.core.gunicorn_worker.ThreadWorkerWithMetrics'
workers = int(os.getenv('GUNICORN_WORKERS', 2))
threads = 4
timeout = 180
graceful_timeout = 185
keepalive = 15
max_requests = 5000
max_requests_jitter = 1000

# Security/SSL
forwarded_allow_ips = '*'
secure_scheme_headers = {'X-FORWARDED-PROTO': 'https'}

# Server mechanics & Debugging
debug = os.getenv('DEBUG', False)
loglevel = os.getenv('GUNICORN_DEBUG', False) and 'debug' or 'info'
statsd_host = 'statsd-exporter:9125'

# Logging
errorlog = '-'
accesslog = '-'
access_log_format = (
    '[%({cf-ipcountry}i)s %({x-forwarded-for}i)s, %(h)s] %(t)s %(r)s [Status %(s)s] %(b)s bytes '
    'from %(f)s %(a)s in %(M)s ms'
)

METRIC_INTERVAL = int(os.environ.get('SATURATION_METRIC_INTERVAL', 1))


class SaturationMonitor(threading.Thread):
    def __init__(self, server: 'Arbiter') -> None:
        super().__init__()
        self.server = server
        self.daemon = True

    def run(self) -> None:
        self.server.log.info(
            f'Started SaturationMonitor with interval {METRIC_INTERVAL}',
        )
        while True:
            self.server.log.debug(
                f'total workers = {self.server.num_workers * threads}',
                extra={
                    'metric': 'gunicorn.total_workers',
                    'value': str(self.server.num_workers * threads),
                    'mtype': 'gauge',
                },
            )
            busy_workers = sum(
                worker.busy.value for worker in self.server.WORKERS.values()
                if worker.busy.value > 0
            )
            self.server.log.debug(
                f'busy workers = {busy_workers}',
                extra={
                    'metric': 'gunicorn.busy_workers',
                    'value': str(busy_workers),
                    'mtype': 'gauge',
                },
            )
            backlog = self.get_backlog()
            if backlog is not None:
                self.server.log.debug(
                    f'request backlog: {backlog}',
                    extra={
                        'metric': 'gunicorn.backlog',
                        'value': str(backlog),
                        'mtype': 'gauge',
                    },
                )
            time.sleep(METRIC_INTERVAL)

    def get_backlog(self) -> int | None:
        """Get the number of connections waiting to be accepted by a server"""
        if not sys.platform == 'linux':
            return None
        total = 0
        for listener in self.server.LISTENERS:
            if not listener.sock:
                continue

            # tcp_info struct from include/uapi/linux/tcp.h
            fmt = 'B' * 8 + 'I' * 24
            tcp_info_struct = listener.sock.getsockopt(
                socket.IPPROTO_TCP,
                socket.TCP_INFO,
                104,
            )
            # 12 is tcpi_unacked
            total += struct.unpack(fmt, tcp_info_struct)[12]

        backlog_inflight_requests = sum(
            (worker.inflight_requests_count.value - threads) for worker in self.server.WORKERS.values()
            if worker.inflight_requests_count.value > threads
        )
        total += backlog_inflight_requests

        return total


def when_ready(server: 'Arbiter') -> None:
    server.log.info('Starting SaturationMonitor')
    sm = SaturationMonitor(server)
    sm.start()
    server.log.debug(
        'busy workers = 0',
        extra={
            'metric': 'gunicorn.busy_workers',
            'value': '0',
            'mtype': 'gauge',
        },
    )
    server.log.debug(
        'total workers = 0',
        extra={
            'metric': 'gunicorn.total_workers',
            'value': str(server.num_workers * threads),
            'mtype': 'gauge',
        },
    )


def post_worker_init(worker: 'ThreadWorkerWithMetrics'):
    import settings.urls  # noqa


def pre_request(worker: 'ThreadWorkerWithMetrics', req: 'Request') -> None:
    worker.busy.value += 1


def post_request(worker: 'ThreadWorkerWithMetrics', req: 'Request', environ: dict, resp: 'Response') -> None:
    worker.busy.value -= 1
    worker.inflight_requests_count.value = len(worker.futures) - 1

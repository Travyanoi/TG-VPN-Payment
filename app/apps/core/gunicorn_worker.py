import ctypes
from multiprocessing import Value
from typing import Any

from gunicorn.workers.gthread import ThreadWorker


class ThreadWorkerWithMetrics(ThreadWorker):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.busy = Value(ctypes.c_uint, 0)
        self.inflight_requests_count = Value(ctypes.c_uint, 0)

    def enqueue_req(self, conn: Any) -> None:
        super().enqueue_req(conn)
        self.inflight_requests_count.value = len(self.futures)

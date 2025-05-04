import uuid
import logging
import time

import redis

from settings.settings import REDIS_PASS
from .errors import (
    BlockTimeExceedError, MutexLockError, MutexUnlockError
)

DEFAULT_BLOCK_TIME = 5
DEFAULT_DELAY = 0.1
DEFAULT_EXPIRY = 7
DEFAULT_CONN = redis.StrictRedis(host="localhost", port=6379, password=REDIS_PASS, db=0)


class RedisMutex(object):
    """Implements mutex using redis
    """

    def __init__(self, redis_conn=DEFAULT_CONN, blocking=True,
                 block_time=DEFAULT_BLOCK_TIME, delay=DEFAULT_DELAY,
                 expiry=DEFAULT_EXPIRY, raise_exception=False):

        if not isinstance(redis_conn, redis.StrictRedis):
            raise TypeError(
                "Connection object must be of type 'redis.StrictRedis', "
                "got '{}' instead".format(type(redis_conn))
            )

        if delay > block_time:
            raise ValueError(
                "Delay for a mutex should always be less than the block time."
            )

        if expiry < block_time:
            raise ValueError(
                "Expiry of a mutex should always be more than the block time."
            )

        self.redis = redis_conn
        self.blocking = blocking
        self.expiry = expiry
        self.raise_exception = raise_exception

        self.__mkey = None
        self.__mvalue = None

        # block_time and delay are not relevant if the
        # mutex is non-blocking, i.e., if blocking=False.
        self.block_time = block_time if self.blocking else None
        self.delay = delay if self.blocking else None

        # Mutex key and mutex value are set to None by default. These
        # are automatically set when a lock is acquired and can be
        # accessed via self.key and self.value
        self.reset()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.release_lock()
        if exception_type:
            raise exception_value

        return self

    @property
    def key(self):
        return self.__mkey

    @property
    def value(self):
        return self.__mvalue

    @staticmethod
    def generate_unique_id():
        return uuid.uuid4().__str__()

    def reset(self):
        self.__mkey = None
        self.__mvalue = None

    def lock(self):
        """Adds the mutex key to redis with the given value and expiry.
        """
        # nx=True ensures that the value must be set only when the
        # provided key does not exist in redis.
        result = self.redis.set(
            self.__mkey, self.__mvalue, nx=True, ex=self.expiry
        )

        if not result:
            raise MutexLockError(
                "Unable to acquire lock using key '{}'".format(self.__mkey)
            )

        return self

    def unlock(self):
        """Deletes the mutex key from redis after validating the unique
        value for mutex.
        """
        stored_value = self.redis.get(self.__mkey)

        # The given key does not exist in redis
        if not stored_value:
            exc_text = f"Unable to unlock. Key {self.__mkey} does not exists in redis."
            if self.raise_exception:
                raise MutexUnlockError(exc_text)
            return logging.error(exc_text)

        # The given value is not equal to the stored value. This is
        # done to remove the lock in a safe way - A lock can only be
        # removed by the process which created it. Read more at
        # https://redis.io/topics/distlock#why-failover-based-implementations-are-not-enough
        elif not stored_value.decode("utf-8") == self.__mvalue:
            exc_text = f"Unable to unlock. Value for key {self.__mkey} was reset."
            if self.raise_exception:
                raise MutexUnlockError(exc_text)

            return logging.error(exc_text)

        self.redis.delete(self.__mkey)
        self.reset()

        return self

    def acquire_lock(self, mutex_key):
        """Handle locking of a mutex.
        """
        self.__mkey = mutex_key
        self.__mvalue = self.generate_unique_id()

        if not self.blocking:
            try:
                return self.lock()
            except MutexLockError:
                self.reset()
                raise MutexLockError(
                    "Unable to acquire lock using key '{}'".format(self.__mkey)
                )

        start = int(time.time())
        elapsed_time = 0

        # Poll redis to acquire lock on the given key for the allowed
        # blocking time
        while elapsed_time < self.block_time:
            try:
                return self.lock()
            except MutexLockError:
                # Add a delay before next poll
                time.sleep(self.delay)
                elapsed_time = int(time.time()) - start

        # Exceeded the allowed waiting time for the mutex and failed
        # to acquire lock in this duration. Hence, raise TimeOutError
        self.reset()
        raise BlockTimeExceedError(
            "Exceeded max allowed block time while acquiring lock."
        )

    def release_lock(self):
        """Handles unlocking of a mutex.
        """
        if not self.__mkey or not self.__mvalue:
            raise MutexUnlockError(
                "Unable to perform operation. Found null values for mutex "
                "key and(or) value."
            )

        return self.unlock()

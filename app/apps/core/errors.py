# errors.py

class RedisMutexError(Exception):
    """Базовое исключение для всех ошибок, связанных с Redis Mutex."""
    pass


class BlockTimeExceedError(RedisMutexError):
    """Исключение, вызываемое при превышении максимального времени ожидания блокировки."""

    def __init__(self, message="Превышено максимальное допустимое время ожидания блокировки."):
        self.message = message
        super().__init__(self.message)


class MutexLockError(RedisMutexError):
    """Исключение, вызываемое при невозможности захватить блокировку."""

    def __init__(self, message="Невозможно захватить блокировку."):
        self.message = message
        super().__init__(self.message)


class MutexUnlockError(RedisMutexError):
    """Исключение, вызываемое при невозможности освободить блокировку."""

    def __init__(self, message="Невозможно освободить блокировку."):
        self.message = message
        super().__init__(self.message)

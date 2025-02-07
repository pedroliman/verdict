from __future__ import annotations

import logging
import signal
from functools import wraps
from typing import Any, Callable, Optional, Type


def keyboard_interrupt_safe(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    @wraps(func)
    def wrapped(self: Any, *args, **kwargs) -> Any:
        original_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, lambda signum, frame: self.executor.graceful_shutdown())

        try:
            return func(self, *args, **kwargs)
        except KeyboardInterrupt:
            self.executor.graceful_shutdown()
        finally:
            signal.signal(signal.SIGINT, original_handler)
    return wrapped

class DisableLogger:
    def __init__(self, logger_name: str, all: bool=False) -> None:
        self.logger = logging.getLogger(logger_name)
        self.previous_level: Optional[int] = None
        self.all = all

    def __enter__(self) -> None:
        self.previous_level = self.logger.level
        new_level = logging.CRITICAL
        if self.all:
            new_level += 1
        self.logger.setLevel(new_level)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.logger.setLevel(self.previous_level) # type: ignore


def lightweight(cls: Type) -> Type:
    cls.lightweight = True
    return cls

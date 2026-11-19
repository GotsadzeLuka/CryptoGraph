"""Bound CPU-intensive RSA work across asyncio event loops in one process.

The limiter prevents arbitrary simultaneous RSA execution within an app worker.
It does not provide distributed rate limiting, request-body caps, or quotas.
"""
from functools import partial
from threading import BoundedSemaphore
from typing import Any, Callable, TypeVar

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

T = TypeVar("T")
_crypto_slots = BoundedSemaphore(value=2)


async def run_limited_crypto(function: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    # Threading primitives are independent of TestClient/event-loop lifetimes.
    # Fail fast rather than allocating a queue of waiting crypto requests.
    if not _crypto_slots.acquire(blocking=False):
        raise HTTPException(status_code=429, detail="Cryptographic worker capacity exceeded")
    try:
        return await run_in_threadpool(partial(function, *args, **kwargs))
    finally:
        _crypto_slots.release()

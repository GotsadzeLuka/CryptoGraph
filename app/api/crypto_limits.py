"""Bound CPU-intensive RSA work across asyncio event loops in one process.

The limiter prevents arbitrary simultaneous RSA execution within an app worker.
It does not provide distributed rate limiting, request-body caps, or quotas.
"""
from asyncio import wrap_future
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore
from typing import Any, Callable, TypeVar

from fastapi import HTTPException
T = TypeVar("T")
_SLOTS = 2
_crypto_slots = BoundedSemaphore(value=_SLOTS)
_executor = ThreadPoolExecutor(max_workers=_SLOTS, thread_name_prefix="cryptograph-rsa")


async def run_limited_crypto(function: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    if not _crypto_slots.acquire(blocking=False):
        raise HTTPException(
            status_code=429,
            detail="Cryptographic worker capacity exceeded",
            headers={"Retry-After": "1"},
        )
    try:
        work = _executor.submit(function, *args, **kwargs)
    except BaseException:
        _crypto_slots.release()
        raise
    # The work can outlive a cancelled HTTP request. Release only when the
    # executor reports that it has completed or cancelled the operation.
    work.add_done_callback(lambda _work: _crypto_slots.release())
    return await wrap_future(work)

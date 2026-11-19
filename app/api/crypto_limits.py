"""Bound expensive RSA execution per process.

Public deployment also requires edge rate limits, proxy request-body limits
and per-instance CPU/memory quotas. This semaphore is not distributed.
"""
import asyncio
from functools import partial
from typing import Any, Callable, TypeVar

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool

T = TypeVar("T")
_crypto_slots = asyncio.Semaphore(2)


async def run_limited_crypto(function: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    try:
        await asyncio.wait_for(_crypto_slots.acquire(), timeout=1.0)
    except TimeoutError as exc:
        raise HTTPException(status_code=429, detail="Cryptographic worker capacity exceeded") from exc
    try:
        return await run_in_threadpool(partial(function, *args, **kwargs))
    finally:
        _crypto_slots.release()

"""ASGI request-size limiter that counts bytes, including chunked uploads.

Rejects oversized declared requests before endpoint invocation and enforces the
same bound while receiving an undeclared/streamed body. This is an application
safety boundary; use proxy-level body limits too for public hosting.
"""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from starlette.responses import JSONResponse


class _TooLarge(Exception):
    pass


class MaxRequestBodyMiddleware:
    def __init__(self, app: Callable[..., Awaitable[None]], max_bytes: int):
        if max_bytes < 1:
            raise ValueError("max_bytes must be positive")
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        length = headers.get(b"content-length")
        if length is not None:
            try:
                declared = int(length)
                if declared < 0:
                    raise ValueError("negative Content-Length")
            except ValueError:
                await self._reject(send, 400, "Invalid Content-Length")
                return
            if declared > self.max_bytes:
                await self._reject(send, 413, "Request body exceeds the upload limit")
                return

        received = 0
        response_started = False

        async def bounded_receive() -> dict[str, Any]:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise _TooLarge()
            return message

        async def guarded_send(message: dict[str, Any]) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, bounded_receive, guarded_send)
        except _TooLarge:
            if response_started:
                # A response already started cannot change HTTP status.
                # Close the transport instead of misreporting a partial success.
                raise
            await self._reject(send, 413, "Request body exceeds the upload limit")

    @staticmethod
    async def _reject(send: Callable, code: int, message: str) -> None:
        response = JSONResponse(
            {"detail": message}, status_code=code,
            headers={"X-Content-Type-Options": "nosniff", "Cache-Control": "no-store"},
        )
        await response({"type": "http", "method": "POST", "path": "/"}, None, send)

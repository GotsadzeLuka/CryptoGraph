"""Security boundary regressions on real FastAPI routes."""
import asyncio
from threading import Event, Lock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.crypto_limits import run_limited_crypto
from app.classical import vigenere
from app.modern import hashing
from main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.parametrize("body,path", [
    ({"text": "x" * 65537}, "/api/modern/hash/sha256"),
    ({"text": "hello", "public_key": "x" * 32769}, "/api/modern/rsa/encrypt"),
    ({"ciphertext": "x" * 8193, "private_key": "invalid"}, "/api/modern/rsa/decrypt"),
    ({"text": "hello", "keyword": "a" * 129}, "/api/classical/vigenere/encrypt"),
    ({"text": "hello", "alphabet": "a" * 257}, "/api/classical/caesar/encrypt"),
])
def test_oversized_fields_rejected_before_crypto(client, body, path):
    assert client.post(path, json=body).status_code == 422


def test_large_declared_body_rejected_early(client):
    response = client.post("/api/modern/rsa/generate-keys",
        content=b"x", headers={"content-length": str(11 * 1024 * 1024)})
    assert response.status_code == 413


def test_private_key_responses_disable_caching(client):
    response = client.post("/api/modern/rsa/generate-keys", json={"key_size": 2048})
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_known_answer_vectors():
    assert vigenere.encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"
    assert hashing.hash_text("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_crypto_admission_control_refuses_overloaded_worker():
    async def scenario():
        blocked, started = Event(), Event()
        lock = Lock()
        count = 0

        def expensive():
            nonlocal count
            with lock:
                count += 1
                if count == 2:
                    started.set()
            blocked.wait(4)

        first = asyncio.create_task(run_limited_crypto(expensive))
        second = asyncio.create_task(run_limited_crypto(expensive))
        try:
            assert await asyncio.to_thread(started.wait, 2), "Both crypto slots must be occupied"
            with pytest.raises(HTTPException) as exc:
                await run_limited_crypto(expensive)
            assert exc.value.status_code == 429
        finally:
            blocked.set()
            await asyncio.gather(first, second)
    asyncio.run(scenario())


def test_existing_openapi_remains_accessible(client):
    assert client.get("/openapi.json").status_code == 200


@pytest.mark.parametrize("declared,status", [("abc",400), ("-1",400), (str(11*1024*1024),413)])
def test_declared_body_limits(client, declared, status):
    response = client.post("/api/modern/hash/sha256", content=b"x", headers={"content-length":declared})
    assert response.status_code == status


def test_streaming_body_without_content_length_is_capped(client):
    # Generator uses Transfer-Encoding: chunked rather than Content-Length.
    def streamed():
        chunk = b"x" * (1024 * 1024)
        for _ in range(12):
            yield chunk

    response = client.post("/api/modern/hash/sha256",
        content=streamed(), headers={"content-type":"application/json"})
    assert response.status_code == 413

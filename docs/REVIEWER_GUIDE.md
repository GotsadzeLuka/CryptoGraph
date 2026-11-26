# Five-minute reviewer guide

**Goal:** Understand what CryptoGraph demonstrates, review the backend design, and verify its central behaviors without relying on a live deployment.

## Minute 1 — Scope and setup

CryptoGraph is a university cryptography lab, not a commercial encryption product. It illustrates **Python/FastAPI, typed API requests, common RSA primitives, custom browser UI and tests**.

```bash
git clone https://github.com/GotsadzeLuka/CryptoGraph.git
cd CryptoGraph
python -m venv .venv
source .venv/bin/activate     # or activate the venv on Windows
python -m pip install --require-hashes -r requirements.txt -r requirements-dev.txt
python -m uvicorn main:app --reload
```

**Hosted demo: offline (former Vercel instance discontinued).** Run the commands above to review locally.

Local UI: `http://localhost:8000/` · Local Swagger: `http://localhost:8000/docs`.

## Minutes 2–3 — Three demonstrations

1. **Historical ciphers:** Encrypt/decrypt "hello" with Caesar; try Vigenère with a keyword and confirm punctuation is preserved.
2. **RSA-OAEP:** Generate a throwaway key pair, encrypt a short message with the public key and decrypt with the private key.
3. **SHA-256 / signatures:** Hash the bundled sample text file, sign a short message and verify the signature using its matching public key; verify that changing the message causes failure.

**Important:** Signing and decryption transmit the PEM private key to the server. Never use real or sensitive keys on an externally hosted instance.

## Minute 4 — Code tour

| Location | What it shows |
| --- | --- |
| `app/api/main.py` | Application factory and routers |
| `app/api/schemas.py` | Pydantic validation and key-size restrictions |
| `app/api/routes_files.py` | File endpoints with 413 response behavior |
| `app/modern/rsa_crypto.py` | RSA-OAEP with standard cryptography library |
| `app/modern/signatures.py` | RSA-PSS signatures |
| `tests/test_api.py` | Contract and end-to-end-in-process HTTP tests |
| `.github/workflows/ci.yml` | Automated quality checks on Python 3.12 and 3.13 |

## Minute 5 — Run verification

```bash
python -m pytest -q tests/
python -m compileall -q app main.py
python -m pip check
```

Check [GitHub Actions](https://github.com/GotsadzeLuka/CryptoGraph/actions) for the latest actual outcome. There is no claim of a successful production deployment.

**Useful interview questions:** Why is RSA padding delegated to a library? Why does the API need an upload cap? Where is the private-key trust boundary? What would change for a production service?

Read [architecture](ARCHITECTURE.md) and [security](../SECURITY.md) for candid tradeoffs.

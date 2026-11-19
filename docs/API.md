# API reference

Run the project locally with `python -m uvicorn main:app --reload`. All examples below use `http://localhost:8000`. The generated OpenAPI specification at `/openapi.json` and interactive Swagger UI at `/docs` are the authoritative request/response definitions.

## Routes

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Service health |
| POST | `/api/classical/caesar/encrypt` | Encrypt by character shift |
| POST | `/api/classical/caesar/decrypt` | Decrypt by character shift |
| POST | `/api/classical/vigenere/encrypt` | Encrypt with repeated keyword |
| POST | `/api/classical/vigenere/decrypt` | Decrypt with keyword |
| POST | `/api/modern/hash/sha256` | SHA-256 of text |
| POST | `/api/modern/rsa/generate-keys` | Generate test RSA PEM pair |
| POST | `/api/modern/rsa/encrypt` | Encrypt short text with RSA-OAEP |
| POST | `/api/modern/rsa/decrypt` | Decrypt RSA-OAEP ciphertext |
| POST | `/api/modern/rsa/sign` | Sign text with RSA-PSS |
| POST | `/api/modern/rsa/verify` | Verify text signature |
| POST | `/api/files/hash` | SHA-256 of uploaded bytes |
| POST | `/api/files/sign` | RSA-PSS sign uploaded bytes |
| POST | `/api/files/verify` | RSA-PSS verify uploaded bytes |

## Quick examples

**Health check**

```bash
curl http://localhost:8000/health
```

**Caesar** — JSON fields: `text` (required), `shift` (default 3), `alphabet` (optional).

```bash
curl -X POST http://localhost:8000/api/classical/caesar/encrypt \
  -H "Content-Type: application/json" \
  -d '{"text":"abc","shift":3}'
```

**Vigenère** — `text` (required), `keyword` (default `cryptolab`).

```bash
curl -X POST http://localhost:8000/api/classical/vigenere/encrypt \
  -H "Content-Type: application/json" \
  -d '{"text":"hello","keyword":"cryptolab"}'
```

**SHA-256**

```bash
curl -X POST http://localhost:8000/api/modern/hash/sha256 \
  -H "Content-Type: application/json" \
  -d '{"text":"hello"}'

curl -X POST http://localhost:8000/api/files/hash \
  -F "file=@sample_data/LukaGotsadze.txt"
```

**RSA key generation** — use only disposable educational keys.

```bash
curl -X POST http://localhost:8000/api/modern/rsa/generate-keys \
  -H "Content-Type: application/json" \
  -d '{"key_size":2048}'
```

Key generation accepts 2048–4096 bits. It returns `private_key` and `public_key` values as unencrypted PEM text in the response; use local test keys only.

## RSA JSON request fields

| Operation | Input fields |
| --- | --- |
| Encrypt | `text`, `public_key` |
| Decrypt | `ciphertext` (Base64), `private_key` |
| Sign text | `text`, `private_key` |
| Verify text | `text`, `signature` (Base64), `public_key` |

**Never use genuine private PEMs** in hosted demos. The API receives them in plaintext at the application layer.

## Multipart file routes

All three `/api/files/*` endpoints accept a `file` field of type uploaded file, limited to **10 MiB**. Signing additionally requires form field `private_key`, and verification requires `signature` plus `public_key`. Example of hashing:

```bash
curl -X POST http://localhost:8000/api/files/hash \
  -F "file=@sample_data/LukaGotsadze.txt"
```

## HTTP behavior

- **200** — valid operation with JSON result.
- **400** — malformed key, signature, or algorithm-specific input where explicitly handled.
- **413** — file larger than the application upload limit.
- **422** — request validation failed, such as missing JSON fields or key size above 4096.
- Other unexpected errors may return **500**; this is not a stabilized public API.

No authentication, service-level availability guarantee or production storage security is implemented. See the [security disclosure](../SECURITY.md).

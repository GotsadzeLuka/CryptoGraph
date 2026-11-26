# CryptoGraph security boundaries

CryptoGraph is a stateless educational lab. Use disposable keys, messages and files in a loopback environment. Signing and decryption receive private PEM values at the application layer.

| Boundary | Behavior |
| --- | --- |
| Historical ciphers | Caesar supports reversible custom alphabets. Vigenère shifts ASCII letters and preserves other characters. |
| RSA | The cryptography library implements RSA-OAEP and RSA-PSS with SHA-256. Keys must be 2048–4096 bits. Malformed values produce controlled errors. |
| Uploads | The application accepts a file up to 10 MiB, with 64 KiB of extra space for multipart framing and metadata. FastAPI counts incoming request bytes before running the operation. |
| Compute | At most two RSA operations run in each process. Additional operations receive HTTP 429. |
| Response handling | POST responses disable caching. Validation errors retain field locations and omit submitted values. |
| Deployment | The container runs as an unprivileged user with bounded concurrent connections. A public service would need authentication, TLS, quotas, and proxy-enforced request limits. |

Runtime and developer packages are locked with hashes. See [CONTRIBUTING.md](../CONTRIBUTING.md) for regeneration and CI checks.

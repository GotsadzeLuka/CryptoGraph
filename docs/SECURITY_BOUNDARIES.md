# Security boundaries and validation

CryptoGraph is an **educational cryptography API**, not a key-management or secure-messaging service. Caesar/Vigenère are insecure classical demonstrations.

- The default Caesar alphabet and Vigenère keyword use ASCII A–Z. Non-Latin letters in text are preserved rather than shifted; they do not consume Vigenère keyword positions. Vigenère keywords must be ASCII letters. Caesar custom alphabets require nonempty, distinct letters and one-to-one case mappings (e.g. Greek is supported).
- RSA operations require RSA keys of at least 2048 bits; generated keys are capped at 4096 bits. RSA-OAEP with SHA-256 encrypts only short plaintexts. PSS with SHA-256 signs data.
- Invalid PEM/key types and malformed Base64 are input errors. A well-formed but incorrect signature returns `valid: false`.
- CPU-intensive RSA operations are offloaded from the event loop to a thread pool, gated by a process-local, two-slot admission guard (HTTP 429 when full). This is not a per-client or distributed rate limit.
- Text endpoints limit fields to 65,536 Unicode characters, keywords to 128 and custom alphabets to 256. Key/encoded-ciphertext fields are bounded. File handlers enforce a 10 MiB per-file read limit. An outer ASGI middleware rejects oversized declared requests and counts actual incoming bytes even when the client streams without Content-Length. It also rejects oversized multipart bodies before cryptographic work begins. Deploy with an additional reverse-proxy request-body limit, upload concurrency quota, edge rate limiting, TLS and instance-level CPU/memory limits. Sensitive crypto responses set no-store.
- Private keys are returned in plaintext only because the project demonstrates local RSA key generation. Do not transmit real production private keys to this API or log/store them.
- CI results must be confirmed from completed GitHub Actions jobs, not inferred from workflow YAML.

## Dependency supply chain

`requirements.txt` pins the direct dependency set and removes unused PyCryptodome. CI performs dependency consistency and installed-environment vulnerability scanning. This is **not yet a fully hashed transitive lock**; the complete dependency graph must be resolved in a clean networked environment for both Python versions and committed only after verification.

ASGI request middleware now caps actual received bytes, including requests with no Content-Length header; enforce proxy limits too.

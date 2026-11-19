# Security boundaries and validation

CryptoGraph is an **educational cryptography API**, not a key-management or secure-messaging service. Caesar/Vigenère are insecure classical demonstrations.

- The default Caesar alphabet and Vigenère keyword use ASCII A–Z. Non-Latin letters in text are preserved rather than shifted; they do not consume Vigenère keyword positions. Vigenère keywords must be ASCII letters. Caesar custom alphabets require nonempty, distinct letters and one-to-one case mappings (e.g. Greek is supported).
- RSA operations require RSA keys of at least 2048 bits; generated keys are capped at 4096 bits. RSA-OAEP with SHA-256 encrypts only short plaintexts. PSS with SHA-256 signs data.
- Invalid PEM/key types and malformed Base64 are input errors. A well-formed but incorrect signature returns `valid: false`.
- CPU-intensive RSA operations are offloaded from the event loop to a thread pool. This does **not** impose a per-client rate limit or CPU quota.
- Text endpoints limit fields to 65,536 Unicode characters. File handlers enforce a 10 MiB per-file read limit. These do not replace a strict reverse-proxy request-body limit, upload concurrency quota, edge rate limiting, TLS, and instance-level CPU/memory limits for public hosting.
- Private keys are returned in plaintext only because the project demonstrates local RSA key generation. Do not transmit real production private keys to this API or log/store them.
- CI results must be confirmed from completed GitHub Actions jobs, not inferred from workflow YAML.

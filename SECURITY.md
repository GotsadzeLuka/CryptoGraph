# Security and responsible usage

**CryptoGraph is an educational cryptography project, not a production encryption, secret-storage or key-management platform.** No independent security audit is claimed.

## The most important limitation

RSA decryption and signing send private PEM material from the browser to the backend, using JSON or form data. Generating keys also returns a private PEM in the HTTP response. **Never use real private keys, credentials or confidential files**, especially with a hosted demo. Use throwaway test values locally.

The app does not deliberately persist users' data or keys in a database. However, HTTP proxies, request logs, browser memory and infrastructure can still expose inputs. This is **not** zero-knowledge or client-side encryption.

## Threat model and controls

| Area | Current behavior |
| --- | --- |
| Caesar / Vigenère | Historical demonstrations, not secure cryptography |
| RSA encryption | RSA-OAEP with SHA-256; short messages only; no hybrid encryption or key lifecycle |
| RSA signing | RSA-PSS with SHA-256 from the Python `cryptography` library |
| Key sizes | RSA generation bounded to **2048–4096 bits** |
| File uploads | Application reads no more than **10 MiB + 1 byte** before accepting/rejecting; returns **413** for oversized uploads |
| Authentication and abuse | No accounts, authentication, rate limiting, quotas or global request-size limits |
| Dependency security | Version *minimums*, not fully pinned/reproducible dependencies |
| Production operations | No monitoring, disaster recovery, incident response programme or hardened key-management layer |

The file read limit reduces application memory pressure; it does not replace multipart parser, load balancer or reverse proxy request limits.

## Safer demo use

- Use local execution and disposable RSA key pairs.
- Never log private PEM data or request bodies.
- Use HTTPS and server-side request-size limits if a demo is hosted.
- Before production exposure, add abuse controls, key isolation/client-side crypto, dependency pinning, secret redaction, operational monitoring and an independent security assessment.
- Do not claim Caesar or Vigenère provide real confidentiality.

## Reporting

Do not post credentials or private keys in public GitHub issues. Use private vulnerability reporting or another private channel if available. No security response SLA is claimed.

See [architecture](docs/ARCHITECTURE.md) and the [reviewer guide](docs/REVIEWER_GUIDE.md).

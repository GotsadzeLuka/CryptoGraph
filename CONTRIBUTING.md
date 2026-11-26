# Contributing and development

CryptoGraph is an educational project. Review and focused contributions are welcome; no response SLA is promised.

## Local checks

Use Python 3.12+ and install requirements in a virtual environment:

```bash
python -m pip install --require-hashes -r requirements.txt -r requirements-dev.txt
python -m pytest -q tests/
python -m compileall -q app main.py
python -m pip check
```

Start a local server with `python -m uvicorn main:app --reload`.

## Coding conventions

- Keep HTTP and Pydantic concerns in `app/api/` and algorithm logic in `app/classical/` or `app/modern/`.
- Write tests for successful operations, invalid inputs and size/complexity limits.
- Use established libraries for modern cryptographic primitives; do not add handwritten RSA padding.
- Never commit or paste real private keys, secret credentials or sensitive user documents.
- Update `docs/API.md`, `docs/ARCHITECTURE.md` and the security disclosure when changing public behavior.

## Pull-request checklist

- Explain the behavior change and the reason.
- Include tests and expected failure behavior.
- Run local quality commands.
- Assess whether the change affects the private-key trust boundary or resource limits.

See the [reviewer guide](docs/REVIEWER_GUIDE.md) and [security disclosure](SECURITY.md).

## Refresh dependency locks

Edit the direct pins in `requirements.in` and `requirements-dev.in`, then run the `uv pip compile` commands at the top of the corresponding lockfiles. Regenerate the runtime lock first. Verify both locks in fresh 3.12 and 3.13 environments with `pip check`, Ruff, pytest, and `python -m pip_audit --require-hashes -r requirements.txt -r requirements-dev.txt`.

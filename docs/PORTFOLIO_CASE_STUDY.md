# CryptoGraph — portfolio case study

**Type:** Educational full-stack Python / FastAPI cryptography application  
**Scope:** University coursework for Security & Cryptography and Web Services and Design

## Problem

Students exploring cryptography need approachable examples that show how text, files, keys, hashes, encryption and signatures fit together. Command-line-only demonstrations hide the API and interaction design.

## Implementation

CryptoGraph combines a browser-based workspace with a typed FastAPI application exposing 14 routes. It demonstrates classical ciphers, SHA-256, RSA-OAEP encryption and RSA-PSS signatures, plus file operations and documentation generated from the API schema.

## Engineering highlights

- Built a Python API with **separated routing, validation, cryptographic and frontend layers**.
- Used **Pydantic request/response schemas** and OpenAPI to make integration verifiable.
- Integrated the established Python **cryptography** package rather than implementing RSA padding manually.
- Wrote a framework-free frontend to demonstrate REST requests and response handling.
- Added unit and HTTP API tests covering correct behavior and error cases.
- Bounded file uploads and RSA key-generation cost to make educational requests more predictable.
- Provided Docker packaging, a CI workflow, a reviewer walkthrough and clear system documentation.

## Decisions and limitations

No database, login, key vault or persistence is implemented: this is a stateless laboratory. Private keys pass through the server for signing and decryption; real-world client-side key security is not provided. The public API also lacks rate limiting and operational security controls.

**This is not a secure production encryption service**, and no deployment uptime, business usage or adoption metrics are claimed.

## Portfolio summary

> Developed CryptoGraph, a Python/FastAPI educational cryptography platform with a custom JavaScript interface. Built REST endpoints for Caesar/Vigenère ciphers, SHA-256 hashing, RSA-OAEP encryption and RSA-PSS signatures, and added pytest coverage, file size validation, Docker support and reviewer-focused documentation.

For evidence, see the [API guide](API.md), [source code](../app), [tests](../tests) and [reviewer guide](REVIEWER_GUIDE.md).

"""Regression tests for input validation and RSA key boundaries."""
import base64

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient

from app.classical import caesar, vigenere
from app.modern import rsa_crypto, signatures
from main import app


@pytest.fixture(scope="module")
def rsa_keys():
    return rsa_crypto.generate_keys()


@pytest.fixture(scope="module")
def ec_keys():
    private = ec.generate_private_key(ec.SECP256R1())
    private_pem = private.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    ).decode()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()
    return private_pem, public_pem


def test_unicode_plaintext_is_preserved_without_consuming_keyword():
    assert vigenere.encrypt("AéB-🙂", "ab") == "AéC-🙂"
    assert caesar.encrypt("AéB-🙂") == "DéE-🙂"


def test_caesar_preserves_letters_outside_the_chosen_alphabet():
    assert caesar.encrypt("K K", shift=1) == "K L"
    assert caesar.encrypt("一二三", shift=1, alphabet="一二三") == "二三一"
    with pytest.raises(ValueError, match="consistently cased or uncased"):
        caesar.encrypt("A", shift=1, alphabet="a一")


@pytest.mark.parametrize("keyword", ["", "é", "κey", "abc1", "a b"])
def test_vigenere_rejects_non_ascii_keywords(keyword):
    with pytest.raises(ValueError):
        vigenere.encrypt("hello", keyword)


@pytest.mark.parametrize("alphabet", ["", "aab", "Aa", "ab1", "a!", "aß", "aς", "aı"])
def test_caesar_rejects_invalid_alphabets(alphabet):
    with pytest.raises(ValueError):
        caesar.encrypt("abc", alphabet=alphabet)


def test_caesar_large_shift_and_unicode_roundtrip():
    text = "Hello, 123! αβΓ"
    for shift in (-10**24, -10**9, 0, 10**9, 10**24):
        assert caesar.decrypt(caesar.encrypt(text, shift=shift), shift=shift) == text


def test_custom_greek_alphabet():
    assert caesar.encrypt("αβΓ!", shift=1, alphabet="αβγ") == "βγΑ!"


def test_rsa_rejects_non_rsa_keys(rsa_keys, ec_keys):
    private, public = rsa_keys
    ec_private, ec_public = ec_keys
    with pytest.raises(ValueError, match="RSA public"):
        rsa_crypto.encrypt("hello", ec_public)
    with pytest.raises(ValueError, match="RSA private"):
        rsa_crypto.decrypt(base64.b64encode(b"hello").decode(), ec_private)
    with pytest.raises(ValueError, match="RSA private"):
        signatures.sign_text("hello", ec_private)
    with pytest.raises(ValueError, match="RSA public"):
        signatures.verify_text("hello", "AA==", ec_public)


def test_base64_validation_and_invalid_signature(rsa_keys):
    private, public = rsa_keys
    with pytest.raises(ValueError, match="base64"):
        rsa_crypto.decrypt("!!!", private)
    with pytest.raises(ValueError, match="base64"):
        signatures.verify_text("hello", "@@@@", public)
    signature = signatures.sign_text("hello", private)
    assert signatures.verify_text("tampered", signature, public) is False
    assert signatures.verify_text("hello", signature, public) is True


def test_api_converts_bad_inputs_to_controlled_errors(rsa_keys, ec_keys):
    private, public = rsa_keys
    ec_private, ec_public = ec_keys
    client = TestClient(app)
    assert client.post("/api/classical/vigenere/encrypt", json={
        "text": "hello", "keyword": "κey",
    }).status_code == 400
    assert client.post("/api/classical/caesar/encrypt", json={
        "text": "hello", "alphabet": "aab",
    }).status_code == 400
    assert client.post("/api/modern/rsa/encrypt", json={
        "text": "hello", "public_key": ec_public,
    }).status_code == 400
    assert client.post("/api/modern/rsa/sign", json={
        "text": "hello", "private_key": ec_private,
    }).status_code == 400
    assert client.post("/api/modern/rsa/decrypt", json={
        "ciphertext": "%%", "private_key": private,
    }).status_code == 400
    assert client.post("/api/modern/rsa/verify", json={
        "text": "hello", "signature": "%%", "public_key": public,
    }).status_code == 400
    assert client.post("/api/modern/hash/sha256", json={
        "text": "x" * 65537,
    }).status_code == 422

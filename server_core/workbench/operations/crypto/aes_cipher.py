import base64
import binascii
import hashlib
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from server_core.workbench.registry import Operation, ParamSpec

MODES = ["encrypt", "decrypt"]
CIPHER_MODES = ["GCM", "CBC"]

_CBC_IV_LEN = 16
_GCM_NONCE_LEN = 12


def _derive_key(passphrase: str) -> bytes:
    return hashlib.sha256(passphrase.encode("utf-8", errors="surrogateescape")).digest()


def _encrypt_cbc(key: bytes, plaintext: bytes) -> bytes:
    iv = os.urandom(_CBC_IV_LEN)
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded = padder.update(plaintext) + padder.finalize()
    encryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    return iv + encryptor.update(padded) + encryptor.finalize()


def _decrypt_cbc(key: bytes, blob: bytes) -> bytes:
    if len(blob) < _CBC_IV_LEN:
        raise ValueError("Ciphertext too short")
    iv, ciphertext = blob[:_CBC_IV_LEN], blob[_CBC_IV_LEN:]
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    try:
        padded = decryptor.update(ciphertext) + decryptor.finalize()
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        return unpadder.update(padded) + unpadder.finalize()
    except ValueError as e:
        raise ValueError(f"Decryption failed (wrong passphrase or corrupt data): {e}")


def _encrypt_gcm(key: bytes, plaintext: bytes) -> bytes:
    nonce = os.urandom(_GCM_NONCE_LEN)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, None)


def _decrypt_gcm(key: bytes, blob: bytes) -> bytes:
    if len(blob) < _GCM_NONCE_LEN:
        raise ValueError("Ciphertext too short")
    nonce, ciphertext = blob[:_GCM_NONCE_LEN], blob[_GCM_NONCE_LEN:]
    try:
        return AESGCM(key).decrypt(nonce, ciphertext, None)
    except InvalidTag:
        raise ValueError("Decryption failed (wrong passphrase or corrupt/tampered data)")


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "encrypt")
    cipher_mode = params.get("cipher_mode", "GCM")
    passphrase = params.get("passphrase", "")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    if cipher_mode not in CIPHER_MODES:
        raise ValueError(f"Unsupported cipher mode: {cipher_mode}")
    if not passphrase:
        raise ValueError("Passphrase must not be empty")

    key = _derive_key(passphrase)

    if mode == "encrypt":
        plaintext = text.encode("utf-8", errors="surrogateescape")
        blob = _encrypt_gcm(key, plaintext) if cipher_mode == "GCM" else _encrypt_cbc(key, plaintext)
        return {"output": base64.b64encode(blob).decode("ascii")}

    try:
        blob = base64.b64decode(text.strip(), validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid Base64 input: {e}")
    plaintext = _decrypt_gcm(key, blob) if cipher_mode == "GCM" else _decrypt_cbc(key, blob)
    return {"output": plaintext.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="aes_cipher",
    category="crypto",
    name="AES Cipher",
    description="AES-256 encrypt/decrypt text with a passphrase-derived key. IV/nonce is generated on encrypt and prepended to the Base64 output.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encrypt"),
        ParamSpec(
            name="cipher_mode",
            label="Cipher Mode",
            type="select",
            choices=CIPHER_MODES,
            default="GCM",
            help_text="GCM is authenticated (recommended); CBC is provided for compatibility.",
        ),
        ParamSpec(
            name="passphrase",
            label="Passphrase",
            type="text",
            required=True,
            help_text="The AES-256 key is derived as SHA-256(passphrase).",
        ),
    ],
)

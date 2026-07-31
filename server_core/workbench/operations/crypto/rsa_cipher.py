import base64
import binascii

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from server_core.workbench.registry import Operation, ParamSpec

MODES = ["encrypt", "decrypt"]

_OAEP_PADDING = padding.OAEP(
    mgf=padding.MGF1(algorithm=hashes.SHA256()),
    algorithm=hashes.SHA256(),
    label=None,
)


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "encrypt")
    pem_key = params.get("pem_key", "").strip()
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    if not pem_key:
        raise ValueError("PEM key must not be empty")

    if mode == "encrypt":
        try:
            public_key = serialization.load_pem_public_key(pem_key.encode("utf-8", errors="surrogateescape"))
        except ValueError as e:
            raise ValueError(f"Invalid PEM public key: {e}")
        plaintext = text.encode("utf-8", errors="surrogateescape")
        try:
            ciphertext = public_key.encrypt(plaintext, _OAEP_PADDING)
        except ValueError as e:
            raise ValueError(f"Encryption failed (input too long for this key size?): {e}")
        return {"output": base64.b64encode(ciphertext).decode("ascii")}

    try:
        private_key = serialization.load_pem_private_key(
            pem_key.encode("utf-8", errors="surrogateescape"), password=None
        )
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid PEM private key: {e}")
    try:
        blob = base64.b64decode(text.strip(), validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid Base64 input: {e}")
    try:
        plaintext = private_key.decrypt(blob, _OAEP_PADDING)
    except ValueError as e:
        raise ValueError(f"Decryption failed (wrong key or corrupt data): {e}")
    return {"output": plaintext.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="rsa_cipher",
    category="crypto",
    name="RSA Cipher (OAEP)",
    description="RSA-OAEP encrypt with a PEM public key, or decrypt with a PEM private key.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encrypt"),
        ParamSpec(
            name="pem_key",
            label="PEM Key",
            type="textarea",
            required=True,
            help_text="Public key to encrypt, private key to decrypt. Use RSA Keypair Generator to create one.",
        ),
    ],
)

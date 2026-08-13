from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from backend.server_core.workbench.registry import Operation, ParamSpec

KEY_SIZES = ["2048", "3072", "4096"]


def run(params: dict) -> dict:
    key_size = params.get("key_size", "2048")
    if key_size not in KEY_SIZES:
        raise ValueError(f"Unsupported key size: {key_size}")

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=int(key_size))
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("ascii")
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("ascii")

    return {
        "output": f"{private_pem}\n{public_pem}",
        "note": "Private key first, then the public key — split on the '-----END PRIVATE KEY-----' line.",
    }


OPERATION = Operation(
    id="rsa_keypair",
    category="crypto",
    name="RSA Keypair Generator",
    description="Generate an RSA private/public keypair in PEM format.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="text", hidden=True),
        ParamSpec(name="key_size", label="Key Size", type="select", choices=KEY_SIZES, default="2048"),
    ],
)

import binascii
import hashlib
import hmac
import json

from backend.server_core.workbench.registry import Operation, ParamSpec

from ._jwt_common import b64url_encode, decode_segment

ALGORITHMS = ["HS256", "HS384", "HS512"]

_HASH_BY_ALG = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}


def run(params: dict) -> dict:
    token = params.get("input", "").strip()
    secret = params.get("secret", "")
    algorithm = params.get("algorithm", "HS256")
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Not a valid JWT (expected header.payload.signature)")
    header_segment, payload_segment, signature_segment = parts

    try:
        header = decode_segment(header_segment)
        payload = decode_segment(payload_segment)
    except (binascii.Error, ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid JWT segment: {e}")

    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")
    digestmod = _HASH_BY_ALG[algorithm]
    expected_signature = b64url_encode(hmac.new(secret.encode("utf-8"), signing_input, digestmod).digest())
    valid = hmac.compare_digest(expected_signature, signature_segment)

    result = {"header": header, "payload": payload, "valid": valid}
    note = f"Signature {'verified' if valid else 'does NOT match'} against {algorithm}."
    return {"output": json.dumps(result, indent=2), "note": note}


OPERATION = Operation(
    id="jwt_verify",
    category="analysis",
    name="JWT Verify",
    description="Verify a JWT's HMAC signature against a secret. A failed verification is a valid result, not an error.",
    run=run,
    params=[
        ParamSpec(name="input", label="Token", type="textarea", required=True),
        ParamSpec(name="secret", label="Secret", type="text", required=True),
        ParamSpec(name="algorithm", label="Algorithm", type="select", choices=ALGORITHMS, default="HS256"),
    ],
)

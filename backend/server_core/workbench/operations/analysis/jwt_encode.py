import hashlib
import hmac
import json

from backend.server_core.workbench.registry import Operation, ParamSpec

from ._jwt_common import b64url_encode

ALGORITHMS = ["HS256", "HS384", "HS512", "none"]

_HASH_BY_ALG = {
    "HS256": hashlib.sha256,
    "HS384": hashlib.sha384,
    "HS512": hashlib.sha512,
}


def run(params: dict) -> dict:
    payload_text = params.get("input", "")
    header_text = params.get("header") or '{"alg":"HS256","typ":"JWT"}'
    secret = params.get("secret", "")
    algorithm = params.get("algorithm", "HS256")
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    try:
        payload = json.loads(payload_text)
        header = json.loads(header_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    header_segment = b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_segment = b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_segment}.{payload_segment}".encode("ascii")

    if algorithm == "none":
        signature_segment = ""
        note = "alg=none token — no signature; only useful for testing servers that fail to reject unsigned tokens."
    else:
        digestmod = _HASH_BY_ALG[algorithm]
        signature = hmac.new(secret.encode("utf-8"), signing_input, digestmod).digest()
        signature_segment = b64url_encode(signature)
        note = None

    result = {"output": f"{header_segment}.{payload_segment}.{signature_segment}"}
    if note:
        result["note"] = note
    return result


OPERATION = Operation(
    id="jwt_encode",
    category="analysis",
    name="JWT Encode",
    description="Build a JWT from a header and payload, signed with an HMAC secret. Supports alg=none for pentest testing.",
    run=run,
    params=[
        ParamSpec(name="input", label="Payload (JSON)", type="textarea", required=True),
        ParamSpec(name="header", label="Header (JSON)", type="textarea", default='{"alg":"HS256","typ":"JWT"}'),
        ParamSpec(name="secret", label="Secret", type="text", help_text="HMAC key. Leave blank when algorithm is 'none'."),
        ParamSpec(name="algorithm", label="Algorithm", type="select", choices=ALGORITHMS, default="HS256"),
    ],
)

import base64
import binascii
import json

from server_core.workbench.registry import Operation, ParamSpec


def _decode_segment(segment: str) -> dict:
    padded = segment + "=" * (-len(segment) % 4)
    raw = base64.urlsafe_b64decode(padded)
    return json.loads(raw)


def run(params: dict) -> dict:
    token = params.get("input", "").strip()
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Not a valid JWT (expected header.payload.signature)")
    try:
        header = _decode_segment(parts[0])
        payload = _decode_segment(parts[1])
    except (binascii.Error, ValueError, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError(f"Invalid JWT segment: {e}")
    result = {"header": header, "payload": payload}
    return {
        "output": json.dumps(result, indent=2),
        "note": "Signature not verified — this only decodes header and payload.",
    }


OPERATION = Operation(
    id="jwt_decode",
    category="analysis",
    name="JWT Decode",
    description="Decode a JWT's header and payload. Does not verify the signature.",
    run=run,
    params=[ParamSpec(name="input", label="Token", type="textarea", required=True)],
)

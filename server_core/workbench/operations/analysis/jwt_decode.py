import binascii
import json

from server_core.workbench.registry import Operation, ParamSpec

from ._jwt_common import decode_segment


def run(params: dict) -> dict:
    token = params.get("input", "").strip()
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Not a valid JWT (expected header.payload.signature)")
    try:
        header = decode_segment(parts[0])
        payload = decode_segment(parts[1])
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

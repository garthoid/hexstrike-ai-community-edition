import base64
import binascii
import zlib

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    try:
        raw = base64.b64decode(text, validate=True)
        decompressed = zlib.decompress(raw)
    except (binascii.Error, ValueError, zlib.error) as e:
        raise ValueError(f"Invalid zlib/Base64 input: {e}")
    return {"output": decompressed.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="zlib_decompress",
    category="compression",
    name="Zlib Decompress",
    description="Decompress Base64-encoded Zlib data.",
    run=run,
    params=[ParamSpec(name="input", label="Base64 Input", type="textarea", required=True)],
)

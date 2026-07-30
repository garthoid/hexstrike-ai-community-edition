import base64
import binascii
import gzip

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    try:
        raw = base64.b64decode(text, validate=True)
        decompressed = gzip.decompress(raw)
    except (binascii.Error, ValueError, OSError) as e:
        raise ValueError(f"Invalid gzip/Base64 input: {e}")
    return {"output": decompressed.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="gzip_decompress",
    category="compression",
    name="Gzip Decompress",
    description="Decompress Base64-encoded Gzip data.",
    run=run,
    params=[ParamSpec(name="input", label="Base64 Input", type="textarea", required=True)],
)

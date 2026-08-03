import base64
import binascii
import gzip

from backend.server_core.workbench.registry import Operation, ParamSpec

MODES = ["compress", "decompress"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "compress")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "compress":
        compressed = gzip.compress(text.encode("utf-8", errors="surrogateescape"))
        return {"output": base64.b64encode(compressed).decode("ascii")}

    stripped = text.strip()
    try:
        raw = base64.b64decode(stripped, validate=True)
        decompressed = gzip.decompress(raw)
    except (binascii.Error, ValueError, OSError) as e:
        raise ValueError(f"Invalid gzip/Base64 input: {e}")
    return {"output": decompressed.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="gzip",
    category="compression",
    name="Gzip",
    description="Gzip-compress text to Base64, or decompress Base64-encoded Gzip data.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="compress"),
    ],
)

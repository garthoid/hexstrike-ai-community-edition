import base64
import binascii
import zlib

from server_core.workbench.registry import Operation, ParamSpec

MODES = ["compress", "decompress"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "compress")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "compress":
        compressed = zlib.compress(text.encode("utf-8", errors="surrogateescape"))
        return {"output": base64.b64encode(compressed).decode("ascii")}

    stripped = text.strip()
    try:
        raw = base64.b64decode(stripped, validate=True)
        decompressed = zlib.decompress(raw)
    except (binascii.Error, ValueError, zlib.error) as e:
        raise ValueError(f"Invalid zlib/Base64 input: {e}")
    return {"output": decompressed.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="zlib",
    category="compression",
    name="Zlib",
    description="Zlib-compress text to Base64, or decompress Base64-encoded Zlib data.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="compress"),
    ],
)

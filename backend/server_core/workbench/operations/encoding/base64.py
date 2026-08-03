import base64
import binascii

from backend.server_core.workbench.registry import Operation, ParamSpec

MODES = ["encode", "decode"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "encode")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "encode":
        encoded = base64.b64encode(text.encode("utf-8", errors="surrogateescape"))
        return {"output": encoded.decode("ascii")}

    stripped = text.strip()
    try:
        padded = stripped + "=" * (-len(stripped) % 4)
        decoded = base64.b64decode(padded, validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid Base64 input: {e}")
    return {"output": decoded.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="base64",
    category="encoding",
    name="Base64",
    description="Encode text as Base64, or decode Base64 back to text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encode"),
    ],
)

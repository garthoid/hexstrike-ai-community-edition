import base64
import binascii

from server_core.workbench.registry import Operation, ParamSpec

MODES = ["encode", "decode"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "encode")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "encode":
        encoded = base64.b32encode(text.encode("utf-8", errors="surrogateescape"))
        return {"output": encoded.decode("ascii")}

    stripped = text.strip().upper()
    padded = stripped + "=" * (-len(stripped) % 8)
    try:
        decoded = base64.b32decode(padded)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid Base32 input: {e}")
    return {"output": decoded.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="base32",
    category="encoding",
    name="Base32",
    description="Encode text as Base32, or decode Base32 back to text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encode"),
    ],
)

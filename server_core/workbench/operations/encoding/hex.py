import binascii

from server_core.workbench.registry import Operation, ParamSpec

MODES = ["encode", "decode"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "encode")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "encode":
        return {"output": text.encode("utf-8", errors="surrogateescape").hex()}

    stripped = "".join(text.split())
    try:
        decoded = binascii.unhexlify(stripped)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid hex input: {e}")
    return {"output": decoded.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="hex",
    category="encoding",
    name="Hex",
    description="Encode text as hexadecimal, or decode hex back to text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encode"),
    ],
)

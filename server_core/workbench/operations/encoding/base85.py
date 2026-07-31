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
        data = text.encode("utf-8", errors="surrogateescape")
        return {"output": base64.a85encode(data).decode("ascii")}

    try:
        raw = base64.a85decode(text.strip().encode("ascii"))
    except (binascii.Error, ValueError, UnicodeEncodeError) as e:
        raise ValueError(f"Invalid Base85/Ascii85 input: {e}")
    return {"output": raw.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="base85",
    category="encoding",
    name="Base85 (Ascii85)",
    description="Base85/Ascii85 encode or decode text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encode"),
    ],
)

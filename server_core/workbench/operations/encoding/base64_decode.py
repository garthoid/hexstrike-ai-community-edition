import base64
import binascii

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    try:
        padded = text + "=" * (-len(text) % 4)
        decoded = base64.b64decode(padded, validate=True)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid Base64 input: {e}")
    return {"output": decoded.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="base64_decode",
    category="encoding",
    name="Base64 Decode",
    description="Decode standard Base64 text.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

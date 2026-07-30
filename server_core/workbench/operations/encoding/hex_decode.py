import binascii

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = "".join(params.get("input", "").split())
    try:
        decoded = binascii.unhexlify(text)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid hex input: {e}")
    return {"output": decoded.decode("utf-8", errors="replace")}


OPERATION = Operation(
    id="hex_decode",
    category="encoding",
    name="Hex Decode",
    description="Decode a hexadecimal string back to text.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    return {"output": text.encode("utf-8", errors="surrogateescape").hex()}


OPERATION = Operation(
    id="hex_encode",
    category="encoding",
    name="Hex Encode",
    description="Encode text as a hexadecimal string.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

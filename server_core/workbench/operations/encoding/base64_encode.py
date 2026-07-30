import base64

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    encoded = base64.b64encode(text.encode("utf-8", errors="surrogateescape"))
    return {"output": encoded.decode("ascii")}


OPERATION = Operation(
    id="base64_encode",
    category="encoding",
    name="Base64 Encode",
    description="Encode text as standard Base64.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

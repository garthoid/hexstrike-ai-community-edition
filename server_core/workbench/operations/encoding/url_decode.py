from urllib.parse import unquote

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    return {"output": unquote(text)}


OPERATION = Operation(
    id="url_decode",
    category="encoding",
    name="URL Decode",
    description="Decode percent-encoded URL text.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

import json

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    return {"output": json.dumps(parsed, separators=(",", ":"))}


OPERATION = Operation(
    id="json_minify",
    category="text",
    name="JSON Minify",
    description="Strip whitespace from JSON, producing the most compact valid form.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

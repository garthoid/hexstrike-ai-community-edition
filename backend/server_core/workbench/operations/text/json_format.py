import json

from backend.server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    try:
        indent = int(params.get("indent", 2))
    except (TypeError, ValueError):
        raise ValueError("Indent must be an integer")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    return {"output": json.dumps(parsed, indent=indent, sort_keys=False)}


OPERATION = Operation(
    id="json_format",
    category="text",
    name="JSON Format",
    description="Pretty-print JSON with indentation.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="indent", label="Indent", type="number", default=2),
    ],
)

from urllib.parse import urlencode

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    lines = [line for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Input must not be empty")

    pairs = []
    for line in lines:
        if "=" not in line:
            raise ValueError(f"Line {line!r} is not in key=value format")
        key, _, value = line.partition("=")
        pairs.append((key.strip(), value.strip()))

    return {"output": urlencode(pairs)}


OPERATION = Operation(
    id="query_string_build",
    category="analysis",
    name="Query String Builder",
    description="Build a URL query string from one key=value pair per line.",
    run=run,
    params=[
        ParamSpec(
            name="input",
            label="Key=Value pairs",
            type="textarea",
            required=True,
            help_text="One pair per line, e.g. a=1",
        ),
    ],
)

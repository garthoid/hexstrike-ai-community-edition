import re

from backend.server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    pattern = params.get("pattern", "")
    flags_param = params.get("flags", "")
    if not pattern:
        raise ValueError("Pattern must not be empty")

    flags = 0
    if "i" in flags_param:
        flags |= re.IGNORECASE
    if "m" in flags_param:
        flags |= re.MULTILINE
    if "s" in flags_param:
        flags |= re.DOTALL

    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}")

    matches = regex.findall(text)
    lines = [m if isinstance(m, str) else "\t".join(m) for m in matches]
    return {"output": "\n".join(lines)}


OPERATION = Operation(
    id="regex_extract",
    category="analysis",
    name="Regex Extract",
    description="Find all matches of a regular expression, one per line.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="pattern", label="Pattern", type="text", required=True),
        ParamSpec(
            name="flags",
            label="Flags",
            type="text",
            default="",
            help_text="Any combination of i (ignorecase), m (multiline), s (dotall).",
        ),
    ],
)

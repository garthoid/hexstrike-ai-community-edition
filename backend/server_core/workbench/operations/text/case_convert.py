import re

from backend.server_core.workbench.registry import Operation, ParamSpec

MODES = ["upper", "lower", "title", "snake_case", "camelCase"]

_WORD_RE = re.compile(r"[A-Za-z0-9]+")


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "upper")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "upper":
        return {"output": text.upper()}
    if mode == "lower":
        return {"output": text.lower()}
    if mode == "title":
        return {"output": text.title()}

    words = _WORD_RE.findall(text)
    if not words:
        return {"output": ""}
    if mode == "snake_case":
        return {"output": "_".join(w.lower() for w in words)}

    first, *rest = words
    return {"output": first.lower() + "".join(w.capitalize() for w in rest)}


OPERATION = Operation(
    id="case_convert",
    category="text",
    name="Case Converter",
    description="Convert text case: upper, lower, title, snake_case, or camelCase.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="upper"),
    ],
)

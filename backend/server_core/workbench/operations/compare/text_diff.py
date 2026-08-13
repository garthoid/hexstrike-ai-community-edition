import difflib

from backend.server_core.workbench.registry import Operation, ParamSpec

MODES = ["unified", "line-by-line"]


def run(params: dict) -> dict:
    text_a = params.get("input", "")
    text_b = params.get("compare", "")
    mode = params.get("mode", "unified")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    if mode == "unified":
        diff = difflib.unified_diff(lines_a, lines_b, fromfile="Text A", tofile="Text B", lineterm="")
        return {"output": "\n".join(diff)}

    lines = []
    for line in difflib.ndiff(lines_a, lines_b):
        lines.append(line)
    return {"output": "\n".join(lines)}


OPERATION = Operation(
    id="text_diff",
    category="compare",
    name="Text Diff",
    description=(
        "Compare two texts and show their differences. Not meaningfully chainable mid-recipe "
        "since it needs two independent texts — 'Text B' is a fixed per-step value, not a chained input."
    ),
    run=run,
    params=[
        ParamSpec(name="input", label="Text A", type="textarea", required=True),
        ParamSpec(
            name="compare",
            label="Text B",
            type="textarea",
            required=True,
            help_text="Compared against Text A. This value is fixed per step, not fed by the previous recipe step.",
        ),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="unified"),
    ],
)

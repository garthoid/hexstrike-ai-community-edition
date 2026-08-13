from backend.server_core.workbench.registry import Operation, ParamSpec

MODES = ["sort", "unique", "reverse"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "sort")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    lines = text.split("\n")
    if mode == "sort":
        lines = sorted(lines)
    elif mode == "unique":
        seen = set()
        deduped = []
        for line in lines:
            if line not in seen:
                seen.add(line)
                deduped.append(line)
        lines = deduped
    else:
        lines = list(reversed(lines))

    return {"output": "\n".join(lines)}


OPERATION = Operation(
    id="line_tools",
    category="text",
    name="Line Tools",
    description="Sort, deduplicate, or reverse newline-delimited lines.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="sort"),
    ],
)

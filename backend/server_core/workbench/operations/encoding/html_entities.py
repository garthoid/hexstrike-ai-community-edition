import html

from backend.server_core.workbench.registry import Operation, ParamSpec

MODES = ["encode", "decode"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "encode")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "decode":
        return {"output": html.unescape(text)}
    return {"output": html.escape(text, quote=True)}


OPERATION = Operation(
    id="html_entities",
    category="encoding",
    name="HTML Entities",
    description="Escape HTML-significant characters as entities, or decode entities back to characters.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encode"),
    ],
)

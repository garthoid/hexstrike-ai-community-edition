from urllib.parse import quote, unquote

from backend.server_core.workbench.registry import Operation, ParamSpec

MODES = ["encode", "decode"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "encode")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    if mode == "decode":
        return {"output": unquote(text)}

    safe = "" if str(params.get("encode_all", "false")).lower() == "true" else "/"
    return {"output": quote(text, safe=safe)}


OPERATION = Operation(
    id="url_encoding",
    category="encoding",
    name="URL Encoding",
    description="Percent-encode text for a URL, or decode percent-encoded text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encode"),
        ParamSpec(
            name="encode_all",
            label="Encode slashes too",
            type="select",
            choices=["false", "true"],
            default="false",
            help_text="Only applies when encoding.",
        ),
    ],
)

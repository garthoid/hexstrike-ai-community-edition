from urllib.parse import quote

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    safe = "" if str(params.get("encode_all", "false")).lower() == "true" else "/"
    return {"output": quote(text, safe=safe)}


OPERATION = Operation(
    id="url_encode",
    category="encoding",
    name="URL Encode",
    description="Percent-encode text for safe use in a URL.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(
            name="encode_all",
            label="Encode slashes too",
            type="select",
            choices=["false", "true"],
            default="false",
        ),
    ],
)

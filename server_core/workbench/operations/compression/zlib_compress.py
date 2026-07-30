import base64
import zlib

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    compressed = zlib.compress(text.encode("utf-8", errors="surrogateescape"))
    return {"output": base64.b64encode(compressed).decode("ascii")}


OPERATION = Operation(
    id="zlib_compress",
    category="compression",
    name="Zlib Compress",
    description="Zlib-compress text, output as Base64.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

import uuid

from server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    version = params.get("version", "4")
    if version == "1":
        return {"output": str(uuid.uuid1())}
    if version == "4":
        return {"output": str(uuid.uuid4())}
    raise ValueError(f"Unsupported UUID version: {version}")


OPERATION = Operation(
    id="uuid_generate",
    category="text",
    name="UUID Generator",
    description="Generate a random (v4) or time-based (v1) UUID. Ignores any input text.",
    run=run,
    params=[
        ParamSpec(
            name="input",
            label="Input",
            type="text",
            help_text="Not used by this operation — kept so it can sit in a recipe.",
        ),
        ParamSpec(name="version", label="Version", type="select", choices=["4", "1"], default="4"),
    ],
)

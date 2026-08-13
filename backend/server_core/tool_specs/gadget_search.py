import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _ropgadget_command(p: dict) -> str:
    argv = ["ROPgadget", "--binary", p["binary"]]
    if p["gadget_type"]:
        argv.append("--only")
        argv.append(p["gadget_type"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="ropgadget",
        mcp_tool_name="ropgadget_search",
        endpoint="/api/tools/ropgadget",
        category="gadget_search",
        description="Search for ROP gadgets in a binary using ROPgadget.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Path to the binary file"),
            ParamSpec("gadget_type", str, default="", help_text="Type of gadgets to search for"),
            ParamSpec("additional_args", str, default="", help_text="Additional ROPgadget arguments"),
        ],
        build_command=_ropgadget_command,
        use_recovery=True,
    ),
]

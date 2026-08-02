import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _volatility_command(p: dict) -> str:
    argv = ["volatility", "-f", p["memory_file"]]
    if p["profile"]:
        argv.append(f"--profile={p['profile']}")
    argv.append(p["plugin"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _volatility3_command(p: dict) -> str:
    argv = ["vol", "-f", p["memory_file"], p["plugin"]]
    if p["output_file"]:
        argv.append("-o")
        argv.append(p["output_file"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="volatility",
        mcp_tool_name="volatility_analyze",
        endpoint="/api/tools/volatility",
        category="memory_forensics",
        description="Execute Volatility for memory forensics analysis with enhanced logging.",
        params=[
            ParamSpec("memory_file", str, required=True, help_text="Path to memory dump file"),
            ParamSpec("plugin", str, required=True, help_text="Volatility plugin to use"),
            ParamSpec("profile", str, default="", help_text="Memory profile to use"),
            ParamSpec("additional_args", str, default="", help_text="Additional Volatility arguments"),
        ],
        build_command=_volatility_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="volatility3",
        mcp_tool_name="volatility3_analyze",
        endpoint="/api/tools/volatility3",
        category="memory_forensics",
        description="Execute Volatility3 for advanced memory forensics with enhanced logging.",
        params=[
            ParamSpec("memory_file", str, required=True, help_text="Path to memory dump file"),
            ParamSpec("plugin", str, required=True, help_text="Volatility3 plugin to execute"),
            ParamSpec("output_file", str, default="", help_text="Output file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional Volatility3 arguments"),
        ],
        build_command=_volatility3_command,
        use_recovery=True,
    ),
]

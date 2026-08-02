import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _uro_command(p: dict) -> str:
    echo_argv = ["echo", p["urls"]]
    uro_argv = ["uro"]
    if p["whitelist"]:
        uro_argv += ["--whitelist", p["whitelist"]]
    if p["blacklist"]:
        uro_argv += ["--blacklist", p["blacklist"]]
    if p["additional_args"]:
        uro_argv += shlex.split(p["additional_args"])
    return shlex.join(echo_argv) + " | " + shlex.join(uro_argv)


SPECS = [
    ToolSpec(
        name="uro",
        mcp_tool_name="uro_url_filtering",
        endpoint="/api/tools/uro",
        category="url_filter",
        description="Execute uro for filtering out similar URLs.",
        params=[
            ParamSpec("urls", str, required=True, help_text="URLs to filter"),
            ParamSpec("whitelist", str, default="", help_text="Whitelist patterns"),
            ParamSpec("blacklist", str, default="", help_text="Blacklist patterns"),
            ParamSpec("additional_args", str, default="", help_text="Additional uro arguments"),
        ],
        build_command=_uro_command,
        use_recovery=True,
    ),
]

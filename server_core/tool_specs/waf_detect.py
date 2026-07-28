from server_core.tool_spec import ParamSpec, ToolSpec


def _wafw00f_command(p: dict) -> str:
    command = f"wafw00f {p['target']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


SPECS = [
    ToolSpec(
        name="wafw00f",
        mcp_tool_name="wafw00f_scan",
        endpoint="/api/tools/wafw00f",
        category="waf_detect",
        description="Execute wafw00f to identify and fingerprint WAF products with enhanced logging.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target URL or IP"),
            ParamSpec("additional_args", str, default="", help_text="Additional wafw00f arguments"),
        ],
        build_command=_wafw00f_command,
        use_recovery=True,
    ),
]

from server_core.tool_spec import ParamSpec, ToolSpec


def _wrap_output(raw, p: dict) -> dict:
    return {"success": True, "output": raw}


def _parsero_command(p: dict) -> str:
    return f"parsero -u {p['target']} {p['additional_args']}"


def _sherlock_command(p: dict) -> str:
    return f"sherlock {p['username']} --output sherlock_results/{p['username']}.json --json"


def _spiderfoot_command(p: dict) -> str:
    return f"spiderfoot -s {p['target']}"


def _sublist3r_command(p: dict) -> str:
    command = f"sublist3r -d {p['domain']} -t {p['threads']}"
    if p["engine"]:
        command += f" -e {p['engine']}"
    return command


SPECS = [
    ToolSpec(
        name="parsero",
        mcp_tool_name="parsero",
        endpoint="/api/tools/osint/parsero",
        category="osint",
        description="Execute Parsero for Robots.txt analysis with enhanced logging.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target URL for Parsero analysis"),
            ParamSpec("additional_args", str, default="", help_text="Optional additional arguments for Parsero"),
        ],
        build_command=_parsero_command,
        postprocess=_wrap_output,
        use_recovery=True,
    ),
    ToolSpec(
        name="sherlock",
        mcp_tool_name="sherlock",
        endpoint="/api/tools/osint/sherlock",
        category="osint",
        description="Execute Sherlock for username investigation across social networks.",
        params=[
            ParamSpec("username", str, required=True, help_text="The username to investigate"),
        ],
        build_command=_sherlock_command,
        postprocess=_wrap_output,
        use_recovery=True,
    ),
    ToolSpec(
        name="spiderfoot",
        mcp_tool_name="spiderfoot",
        endpoint="/api/tools/osint/spiderfoot",
        category="osint",
        description="Execute SpiderFoot for OSINT automation with enhanced logging.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target domain or IP for SpiderFoot analysis"),
        ],
        build_command=_spiderfoot_command,
        postprocess=_wrap_output,
        use_recovery=True,
    ),
    ToolSpec(
        name="sublist3r",
        mcp_tool_name="sublist3r",
        endpoint="/api/tools/osint/sublist3r",
        category="osint",
        description="Execute Sublist3r for subdomain enumeration with enhanced logging.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain for subdomain enumeration"),
            ParamSpec("threads", int, default=3, help_text="Number of threads to use (default: 3)"),
            ParamSpec("engine", str, default="", help_text='Optional search engine to use (e.g., "google", "bing")'),
        ],
        build_command=_sublist3r_command,
        postprocess=_wrap_output,
        use_recovery=True,
    ),
]

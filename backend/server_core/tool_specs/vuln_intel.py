import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _vulnx_command(p: dict) -> str:
    cve_id, search, auth = p["cve_id"], p["search"], p["auth_key"]
    if not (cve_id or search):
        raise ToolValidationError("At least one of cve_id or search must be provided")

    argv = ["vulnx"]
    if cve_id:
        argv.append("id")
        argv.append(cve_id)
    if search:
        argv.append("search")
        argv.append(search)
    if auth:
        argv.append("auth")
        argv.append("--api-key")
        argv.append(auth)
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="vulnx",
        mcp_tool_name="vulnx",
        endpoint="/api/vuln-intel/vulnx",
        category="vuln_intel",
        description="CVE vulnerability intelligence and analysis using vulnx.",
        params=[
            ParamSpec("cve_id", str, default="", help_text="CVE identifier (optional)"),
            ParamSpec("search", str, default="", help_text="Search string (optional)"),
            ParamSpec("auth_key", str, default="", help_text="API authentication key (optional)"),
        ],
        build_command=_vulnx_command,
        use_recovery=True,
    ),
]

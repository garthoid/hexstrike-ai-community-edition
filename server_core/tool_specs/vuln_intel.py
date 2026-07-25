from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _vulnx_command(p: dict) -> str:
    cve_id, search, auth = p["cve_id"], p["search"], p["auth_key"]
    if not (cve_id or search):
        raise ToolValidationError("At least one of cve_id or search must be provided")

    command = "vulnx"
    if cve_id:
        command += f" id {cve_id}"
    if search:
        command += f' search "{search}"'
    if auth:
        command += f' auth --api-key "{auth}"'
    return command


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

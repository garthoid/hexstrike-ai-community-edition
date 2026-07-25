from server_core.tool_spec import ParamSpec, ToolSpec


def _nuclei_command(p: dict) -> str:
    command = f"nuclei -u {p['target']}"
    if p["severity"]:
        command += f" -severity {p['severity']}"
    if p["tags"]:
        command += f" -tags {p['tags']}"
    if p["template"]:
        command += f" -t {p['template']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


SPECS = [
    ToolSpec(
        name="nuclei",
        mcp_tool_name="nuclei_scan",
        endpoint="/api/tools/nuclei",
        category="vuln_scan",
        description="Execute Nuclei vulnerability scanner with enhanced logging and real-time progress.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target URL or IP"),
            ParamSpec("severity", str, default="", help_text="Filter by severity (critical,high,medium,low,info)"),
            ParamSpec("tags", str, default="", help_text="Filter by tags (e.g. cve,rce,lfi)"),
            ParamSpec("template", str, default="", help_text="Custom template path"),
            ParamSpec("additional_args", str, default="", help_text="Additional Nuclei arguments"),
        ],
        build_command=_nuclei_command,
        use_recovery=True,
    ),
]

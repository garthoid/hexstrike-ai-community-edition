import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _nuclei_command(p: dict) -> str:
    argv = ["nuclei", "-u", p["target"]]
    if p["severity"]:
        argv.append("-severity")
        argv.append(p["severity"])
    if p["tags"]:
        argv.append("-tags")
        argv.append(p["tags"])
    if p["template"]:
        argv.append("-t")
        argv.append(p["template"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


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

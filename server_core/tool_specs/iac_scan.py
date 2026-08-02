import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _checkov_command(p: dict) -> str:
    argv = ["checkov", "-d", p["directory"]]
    if p["framework"]:
        argv.append("--framework")
        argv.append(p["framework"])
    if p["check"]:
        argv.append("--check")
        argv.append(p["check"])
    if p["skip_check"]:
        argv.append("--skip-check")
        argv.append(p["skip_check"])
    if p["output_format"]:
        argv.append("--output")
        argv.append(p["output_format"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _terrascan_command(p: dict) -> str:
    argv = ["terrascan", "scan", "-t", p["scan_type"], "-d", p["iac_dir"]]
    if p["policy_type"]:
        argv.append("-p")
        argv.append(p["policy_type"])
    if p["output_format"]:
        argv.append("-o")
        argv.append(p["output_format"])
    if p["severity"]:
        argv.append("--severity")
        argv.append(p["severity"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="checkov",
        mcp_tool_name="checkov_iac_scan",
        endpoint="/api/tools/checkov",
        category="iac_scan",
        description="Execute Checkov for infrastructure as code security scanning.",
        params=[
            ParamSpec("directory", str, default=".", help_text="Directory to scan"),
            ParamSpec("framework", str, default="",
                      help_text="Framework to scan (terraform, cloudformation, kubernetes, etc.)"),
            ParamSpec("check", str, default="", help_text="Specific check to run"),
            ParamSpec("skip_check", str, default="", help_text="Check to skip"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, yaml, cli)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Checkov arguments"),
        ],
        build_command=_checkov_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="terrascan",
        mcp_tool_name="terrascan_iac_scan",
        endpoint="/api/tools/terrascan",
        category="iac_scan",
        description="Execute Terrascan for infrastructure as code security scanning.",
        params=[
            ParamSpec("scan_type", str, default="all", help_text="Type of scan (all, terraform, k8s, etc.)"),
            ParamSpec("iac_dir", str, default=".", help_text="Infrastructure as code directory"),
            ParamSpec("policy_type", str, default="", help_text="Policy type to use"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, yaml, xml)"),
            ParamSpec("severity", str, default="", help_text="Severity filter (high, medium, low)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Terrascan arguments"),
        ],
        build_command=_terrascan_command,
        use_recovery=True,
    ),
]

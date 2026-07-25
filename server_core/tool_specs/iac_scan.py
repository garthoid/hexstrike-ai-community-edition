from server_core.tool_spec import ParamSpec, ToolSpec


def _checkov_command(p: dict) -> str:
    parts = [f"checkov -d {p['directory']}"]
    if p["framework"]:
        parts.append(f"--framework {p['framework']}")
    if p["check"]:
        parts.append(f"--check {p['check']}")
    if p["skip_check"]:
        parts.append(f"--skip-check {p['skip_check']}")
    if p["output_format"]:
        parts.append(f"--output {p['output_format']}")
    if p["additional_args"]:
        parts.append(p["additional_args"])
    return " ".join(parts)


def _terrascan_command(p: dict) -> str:
    parts = [f"terrascan scan -t {p['scan_type']} -d {p['iac_dir']}"]
    if p["policy_type"]:
        parts.append(f"-p {p['policy_type']}")
    if p["output_format"]:
        parts.append(f"-o {p['output_format']}")
    if p["severity"]:
        parts.append(f"--severity {p['severity']}")
    if p["additional_args"]:
        parts.append(p["additional_args"])
    return " ".join(parts)


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

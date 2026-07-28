from pathlib import Path

from server_core.tool_spec import ParamSpec, ToolSpec


def _prowler_command(p: dict) -> str:
    Path(p["output_dir"]).mkdir(parents=True, exist_ok=True)

    parts = [f"prowler {p['provider']}"]
    if p["profile"]:
        parts.append(f"--profile {p['profile']}")
    if p["region"]:
        parts.append(f"--region {p['region']}")
    if p["checks"]:
        parts.append(f"--checks {p['checks']}")
    parts.append(f"--output-directory {p['output_dir']}")
    parts.append(f"--output-format {p['output_format']}")
    if p["additional_args"]:
        parts.append(p["additional_args"])
    return " ".join(parts)


def _prowler_postprocess(raw: dict, p: dict) -> dict:
    raw["output_directory"] = p["output_dir"]
    return raw


def _scout_suite_command(p: dict) -> str:
    Path(p["report_dir"]).mkdir(parents=True, exist_ok=True)

    parts = [f"scout {p['provider']}"]
    if p["profile"] and p["provider"] == "aws":
        parts.append(f"--profile {p['profile']}")
    if p["services"]:
        parts.append(f"--services {p['services']}")
    if p["exceptions"]:
        parts.append(f"--exceptions {p['exceptions']}")
    parts.append(f"--report-dir {p['report_dir']}")
    if p["additional_args"]:
        parts.append(p["additional_args"])
    return " ".join(parts)


def _scout_suite_postprocess(raw: dict, p: dict) -> dict:
    raw["report_directory"] = p["report_dir"]
    return raw


SPECS = [
    ToolSpec(
        name="prowler",
        mcp_tool_name="prowler_scan",
        endpoint="/api/tools/prowler",
        category="cloud_audit",
        description="Execute Prowler for comprehensive cloud security assessment.",
        params=[
            ParamSpec("provider", str, default="aws", help_text="Cloud provider (aws, azure, gcp)"),
            ParamSpec("profile", str, default="default", help_text="AWS profile to use"),
            ParamSpec("region", str, default="", help_text="Specific region to scan"),
            ParamSpec("checks", str, default="", help_text="Specific checks to run"),
            ParamSpec("output_dir", str, default="/tmp/prowler_output", help_text="Directory to save results"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, csv, html)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Prowler arguments"),
        ],
        build_command=_prowler_command,
        postprocess=_prowler_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="scout-suite",
        mcp_tool_name="scout_suite_assessment",
        endpoint="/api/tools/scout-suite",
        category="cloud_audit",
        description="Execute Scout Suite for multi-cloud security assessment.",
        params=[
            ParamSpec("provider", str, default="aws", help_text="Cloud provider (aws, azure, gcp, aliyun, oci)"),
            ParamSpec("profile", str, default="default", help_text="AWS profile to use"),
            ParamSpec("report_dir", str, default="/tmp/scout-suite", help_text="Directory to save reports"),
            ParamSpec("services", str, default="", help_text="Specific services to assess"),
            ParamSpec("exceptions", str, default="", help_text="Exceptions file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional Scout Suite arguments"),
        ],
        build_command=_scout_suite_command,
        postprocess=_scout_suite_postprocess,
        use_recovery=True,
    ),
]

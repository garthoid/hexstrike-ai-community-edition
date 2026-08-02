import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _falco_command(p: dict) -> str:
    argv = ["timeout", str(p["duration"]), "falco"]
    if p["config_file"]:
        argv.append("--config")
        argv.append(p["config_file"])
    if p["rules_file"]:
        argv.append("--rules")
        argv.append(p["rules_file"])
    if p["output_format"] == "json":
        argv.append("--json")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="falco",
        mcp_tool_name="falco_runtime_monitoring",
        endpoint="/api/tools/falco",
        category="runtime_monitor",
        description="Execute Falco for runtime security monitoring.",
        params=[
            ParamSpec("config_file", str, default="/etc/falco/falco.yaml", help_text="Falco configuration file"),
            ParamSpec("rules_file", str, default="", help_text="Custom rules file"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, text)"),
            ParamSpec("duration", int, default=60, help_text="Monitoring duration in seconds"),
            ParamSpec("additional_args", str, default="", help_text="Additional Falco arguments"),
        ],
        build_command=_falco_command,
    ),
]

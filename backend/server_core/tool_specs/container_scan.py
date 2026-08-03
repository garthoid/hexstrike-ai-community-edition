import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _trivy_command(p: dict) -> str:
    argv = ["trivy", p["scan_type"], p["target"]]
    if p["output_format"]:
        argv.append("--format")
        argv.append(p["output_format"])
    if p["severity"]:
        argv.append("--severity")
        argv.append(p["severity"])
    if p["output_file"]:
        argv.append("--output")
        argv.append(p["output_file"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _trivy_postprocess(raw: dict, params: dict) -> dict:
    if params["output_file"]:
        raw["output_file"] = params["output_file"]
    return raw


def _docker_bench_command(p: dict) -> str:
    argv = ["docker-bench-security"]
    if p["checks"]:
        argv.append("-c")
        argv.append(p["checks"])
    if p["exclude"]:
        argv.append("-e")
        argv.append(p["exclude"])
    if p["output_file"]:
        argv.append("-l")
        argv.append(p["output_file"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _docker_bench_postprocess(raw: dict, params: dict) -> dict:
    raw["output_file"] = params["output_file"]
    return raw


def _clair_command(p: dict) -> str:
    argv = ["clairctl", "analyze", p["image"]]
    if p["config"]:
        argv.append("--config")
        argv.append(p["config"])
    if p["output_format"]:
        argv.append("--format")
        argv.append(p["output_format"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="trivy",
        mcp_tool_name="trivy_scan",
        endpoint="/api/tools/trivy",
        category="container_scan",
        description="Execute Trivy for container and filesystem vulnerability scanning.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target to scan (image name, directory, repository)"),
            ParamSpec("scan_type", str, default="image", help_text="Type of scan (image, fs, repo, config)"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, table, sarif)"),
            ParamSpec("severity", str, default="", help_text="Severity filter (UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL)"),
            ParamSpec("output_file", str, default="", help_text="File to save results"),
            ParamSpec("additional_args", str, default="", help_text="Additional Trivy arguments"),
        ],
        build_command=_trivy_command,
        postprocess=_trivy_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="docker-bench-security",
        mcp_tool_name="docker_bench_security_scan",
        endpoint="/api/tools/docker-bench-security",
        category="container_scan",
        description="Execute Docker Bench for Security for Docker security assessment.",
        params=[
            ParamSpec("checks", str, default="", help_text="Specific checks to run"),
            ParamSpec("exclude", str, default="", help_text="Checks to exclude"),
            ParamSpec("output_file", str, default="/tmp/docker-bench-results.json", help_text="Output file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional Docker Bench arguments"),
        ],
        build_command=_docker_bench_command,
        postprocess=_docker_bench_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="clair",
        mcp_tool_name="clair_vulnerability_scan",
        endpoint="/api/tools/clair",
        category="container_scan",
        description="Execute Clair for container vulnerability analysis.",
        params=[
            ParamSpec("image", str, required=True, help_text="Container image to scan"),
            ParamSpec("config", str, default="/etc/clair/config.yaml", help_text="Clair configuration file"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, yaml)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Clair arguments"),
        ],
        build_command=_clair_command,
        use_recovery=True,
    ),
]

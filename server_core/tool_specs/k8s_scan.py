import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _kube_bench_command(p: dict) -> str:
    argv = ["kube-bench"]
    if p["targets"]:
        argv.append("--targets")
        argv.append(p["targets"])
    if p["version"]:
        argv.append("--version")
        argv.append(p["version"])
    if p["config_dir"]:
        argv.append("--config-dir")
        argv.append(p["config_dir"])
    if p["output_format"]:
        argv.append("--outputfile")
        argv.append(f"/tmp/kube-bench-results.{p['output_format']}")
        argv.append("--json")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _kube_hunter_command(p: dict) -> str:
    argv = ["kube-hunter"]
    if p["target"]:
        argv.append("--remote")
        argv.append(p["target"])
    elif p["remote"]:
        argv.append("--remote")
        argv.append(p["remote"])
    elif p["cidr"]:
        argv.append("--cidr")
        argv.append(p["cidr"])
    elif p["interface"]:
        argv.append("--interface")
        argv.append(p["interface"])
    else:
        argv.append("--pod")

    if p["active"]:
        argv.append("--active")
    if p["report"]:
        argv.append("--report")
        argv.append(p["report"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="kube-bench",
        mcp_tool_name="kube_bench_cis",
        endpoint="/api/tools/kube-bench",
        category="k8s_scan",
        description="Execute kube-bench for CIS Kubernetes benchmark checks.",
        params=[
            ParamSpec("targets", str, default="", help_text="Targets to check (master, node, etcd, policies)"),
            ParamSpec("version", str, default="", help_text="Kubernetes version"),
            ParamSpec("config_dir", str, default="", help_text="Configuration directory"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, yaml)"),
            ParamSpec("additional_args", str, default="", help_text="Additional kube-bench arguments"),
        ],
        build_command=_kube_bench_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="kube-hunter",
        mcp_tool_name="kube_hunter_scan",
        endpoint="/api/tools/kube-hunter",
        category="k8s_scan",
        description="Execute kube-hunter for Kubernetes penetration testing.",
        params=[
            ParamSpec("target", str, default="", help_text="Specific target to scan"),
            ParamSpec("remote", str, default="", help_text="Remote target to scan"),
            ParamSpec("cidr", str, default="", help_text="CIDR range to scan"),
            ParamSpec("interface", str, default="", help_text="Network interface to scan"),
            ParamSpec("active", bool, default=False, help_text="Enable active hunting (potentially harmful)"),
            ParamSpec("report", str, default="json", help_text="Report format (json, yaml)"),
            ParamSpec("additional_args", str, default="", help_text="Additional kube-hunter arguments"),
        ],
        build_command=_kube_hunter_command,
        use_recovery=True,
    ),
]

from server_core.tool_spec import ParamSpec, ToolSpec


def _kube_bench_command(p: dict) -> str:
    parts = ["kube-bench"]
    if p["targets"]:
        parts.append(f"--targets {p['targets']}")
    if p["version"]:
        parts.append(f"--version {p['version']}")
    if p["config_dir"]:
        parts.append(f"--config-dir {p['config_dir']}")
    if p["output_format"]:
        parts.append(f"--outputfile /tmp/kube-bench-results.{p['output_format']} --json")
    if p["additional_args"]:
        parts.append(p["additional_args"])
    return " ".join(parts)


def _kube_hunter_command(p: dict) -> str:
    parts = ["kube-hunter"]
    if p["target"]:
        parts.append(f"--remote {p['target']}")
    elif p["remote"]:
        parts.append(f"--remote {p['remote']}")
    elif p["cidr"]:
        parts.append(f"--cidr {p['cidr']}")
    elif p["interface"]:
        parts.append(f"--interface {p['interface']}")
    else:
        parts.append("--pod")

    if p["active"]:
        parts.append("--active")
    if p["report"]:
        parts.append(f"--report {p['report']}")
    if p["additional_args"]:
        parts.append(p["additional_args"])
    return " ".join(parts)


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

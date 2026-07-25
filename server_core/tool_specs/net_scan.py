from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _arp_scan_command(p: dict) -> str:
    if not p["target"] and not p["local_network"]:
        raise ToolValidationError("Target parameter or local_network flag is required")

    command = f"arp-scan -t {p['timeout']} -r {p['retry']}"
    if p["interface"]:
        command += f" -I {p['interface']}"
    if p["local_network"]:
        command += " -l"
    else:
        command += f" {p['target']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _masscan_command(p: dict) -> str:
    command = f"masscan {p['target']} -p{p['ports']} --rate={p['rate']}"
    if p["interface"]:
        command += f" -e {p['interface']}"
    if p["router_mac"]:
        command += f" --router-mac {p['router_mac']}"
    if p["source_ip"]:
        command += f" --source-ip {p['source_ip']}"
    if p["banners"]:
        command += " --banners"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _rustscan_command(p: dict) -> str:
    command = f"rustscan -a {p['target']} --ulimit {p['ulimit']} -b {p['batch_size']} -t {p['timeout']}"
    if p["ports"]:
        command += f" -p {p['ports']}"
    if p["scripts"]:
        command += " -- -sC -sV"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _nmap_command(p: dict) -> str:
    command = f"nmap {p['scan_type']}"
    if p["ports"]:
        command += f" -p {p['ports']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += f" {p['target']}"
    return command


def _nmap_advanced_command(p: dict) -> str:
    command = f"nmap {p['scan_type']} {p['target']}"
    if p["ports"]:
        command += f" -p {p['ports']}"
    if p["stealth"]:
        command += " -T2 -f --mtu 24"
    else:
        command += f" -{p['timing']}"
    if p["os_detection"]:
        command += " -O"
    if p["version_detection"]:
        command += " -sV"
    if p["aggressive"]:
        command += " -A"
    if p["nse_scripts"]:
        command += f" --script={p['nse_scripts']}"
    elif not p["aggressive"]:
        command += " -sC"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


SPECS = [
    ToolSpec(
        name="arp-scan",
        mcp_tool_name="arp_scan_discovery",
        endpoint="/api/tools/arp-scan",
        category="net_scan",
        description="Execute arp-scan for network discovery.",
        params=[
            ParamSpec("target", str, default="", help_text="The target IP range (if not using local_network)"),
            ParamSpec("interface", str, default="", help_text="Network interface to use"),
            ParamSpec("local_network", bool, default=False, help_text="Scan local network"),
            ParamSpec("timeout", int, default=500, help_text="Timeout in milliseconds"),
            ParamSpec("retry", int, default=3, help_text="Number of retries"),
            ParamSpec("additional_args", str, default="", help_text="Additional arp-scan arguments"),
        ],
        build_command=_arp_scan_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="masscan",
        mcp_tool_name="masscan_high_speed",
        endpoint="/api/tools/masscan",
        category="net_scan",
        description="Execute Masscan for high-speed Internet-scale port scanning.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address or CIDR range"),
            ParamSpec("ports", str, default="1-65535", help_text="Port range to scan"),
            ParamSpec("rate", int, default=1000, help_text="Packets per second rate"),
            ParamSpec("interface", str, default="", help_text="Network interface to use"),
            ParamSpec("router_mac", str, default="", help_text="Router MAC address"),
            ParamSpec("source_ip", str, default="", help_text="Source IP address"),
            ParamSpec("banners", bool, default=False, help_text="Enable banner grabbing"),
            ParamSpec("additional_args", str, default="", help_text="Additional Masscan arguments"),
        ],
        build_command=_masscan_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="rustscan",
        mcp_tool_name="rustscan_fast_scan",
        endpoint="/api/tools/rustscan",
        category="net_scan",
        description="Execute Rustscan for ultra-fast port scanning.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address or hostname"),
            ParamSpec("ports", str, default="", help_text="Specific ports to scan (e.g., \"22,80,443\")"),
            ParamSpec("ulimit", int, default=5000, help_text="File descriptor limit"),
            ParamSpec("batch_size", int, default=4500, help_text="Batch size for scanning"),
            ParamSpec("timeout", int, default=1500, help_text="Timeout in milliseconds"),
            ParamSpec("scripts", bool, default=False, help_text="Run Nmap scripts on discovered ports"),
            ParamSpec("additional_args", str, default="", help_text="Additional Rustscan arguments"),
        ],
        build_command=_rustscan_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="nmap",
        mcp_tool_name="nmap_scan",
        endpoint="/api/tools/nmap",
        category="net_scan",
        description="Execute an Nmap scan against a target.",
        params=[
            ParamSpec("target", str, required=True, help_text="The IP address or hostname to scan"),
            ParamSpec("scan_type", str, default="-sCV", help_text="Scan type (e.g., -sV for version detection, -sC for scripts)"),
            ParamSpec("ports", str, default="", help_text="Comma-separated list of ports or port ranges"),
            ParamSpec("additional_args", str, default="-T4 -Pn", help_text="Additional Nmap arguments"),
        ],
        build_command=_nmap_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="nmap-advanced",
        mcp_tool_name="nmap_advanced_scan",
        endpoint="/api/tools/nmap-advanced",
        category="net_scan",
        description="Execute advanced Nmap scans with custom NSE scripts and optimized timing.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address or hostname"),
            ParamSpec("scan_type", str, default="-sS", help_text="Nmap scan type (e.g., -sS, -sT, -sU)"),
            ParamSpec("ports", str, default="", help_text="Specific ports to scan"),
            ParamSpec("timing", str, default="T4", help_text="Timing template (T0-T5)"),
            ParamSpec("nse_scripts", str, default="", help_text="Custom NSE scripts to run"),
            ParamSpec("os_detection", bool, default=False, help_text="Enable OS detection"),
            ParamSpec("version_detection", bool, default=False, help_text="Enable version detection"),
            ParamSpec("aggressive", bool, default=False, help_text="Enable aggressive scanning"),
            ParamSpec("stealth", bool, default=False, help_text="Enable stealth mode"),
            ParamSpec("additional_args", str, default="", help_text="Additional Nmap arguments"),
        ],
        build_command=_nmap_advanced_command,
        use_recovery=True,
    ),
]

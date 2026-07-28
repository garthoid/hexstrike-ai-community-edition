from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _amass_command(p: dict) -> str:
    command = f"amass {p['mode']} -d {p['domain']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _assetfinder_command(p: dict) -> str:
    command = "assetfinder"
    if p["only_subdomains"]:
        command += " --subs-only"
    command += f" {p['domain']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _autorecon_command(p: dict) -> str:
    command = f"autorecon {p['target']} -o {p['output_dir']} --heartbeat {p['heartbeat']} --timeout {p['timeout']}"
    if p["port_scans"] != "default":
        command += f" --port-scans {p['port_scans']}"
    if p["service_scans"] != "default":
        command += f" --service-scans {p['service_scans']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _massdns_command(p: dict) -> str:
    if not p["domainlist"] and not p["resolvers"] and not p["additional_args"]:
        raise ToolValidationError("domainlist is required (path to input names file)")
    if p["status_format"] and p["status_format"] not in {"json", "ansi"}:
        raise ToolValidationError("status_format must be either 'json' or 'ansi'")

    command_parts = ["massdns"]
    if p["bindto"]:
        command_parts.extend(["-b", p["bindto"]])
    if p["busy_poll"]:
        command_parts.append("--busy-poll")
    if p["resolve_count"]:
        command_parts.extend(["-c", str(p["resolve_count"])])
    if p["drop_group"]:
        command_parts.extend(["--drop-group", p["drop_group"]])
    if p["drop_user"]:
        command_parts.extend(["--drop-user", p["drop_user"]])
    if p["extended_input"]:
        command_parts.append("--extended-input")
    if p["filter"]:
        command_parts.extend(["--filter", str(p["filter"])])
    if p["flush"]:
        command_parts.append("--flush")
    if p["ignore"]:
        command_parts.extend(["--ignore", str(p["ignore"])])
    if p["interval"]:
        command_parts.extend(["-i", str(p["interval"])])
    if p["error_log"]:
        command_parts.extend(["-l", p["error_log"]])
    if p["norecurse"]:
        command_parts.append("--norecurse")
    if p["output"]:
        command_parts.extend(["-o", p["output"]])
    if p["predictable"]:
        command_parts.append("--predictable")
    if p["processes"]:
        command_parts.extend(["--processes", str(p["processes"])])
    if p["quiet"]:
        command_parts.append("-q")
    if p["rand_src_ipv6"]:
        command_parts.extend(["--rand-src-ipv6", p["rand_src_ipv6"]])
    if p["rcvbuf"]:
        command_parts.extend(["--rcvbuf", str(p["rcvbuf"])])
    if p["retry"]:
        command_parts.extend(["--retry", str(p["retry"])])
    if p["resolvers"]:
        command_parts.extend(["-r", p["resolvers"]])
    if p["root"]:
        command_parts.append("--root")
    if p["hashmap_size"]:
        command_parts.extend(["-s", str(p["hashmap_size"])])
    if p["sndbuf"]:
        command_parts.extend(["--sndbuf", str(p["sndbuf"])])
    if p["status_format"]:
        command_parts.extend(["--status-format", p["status_format"]])
    if p["sticky"]:
        command_parts.append("--sticky")
    if p["socket_count"]:
        command_parts.extend(["--socket-count", str(p["socket_count"])])
    if p["record_type"]:
        command_parts.extend(["-t", p["record_type"]])
    if p["verify_ip"]:
        command_parts.append("--verify-ip")
    if p["outfile"]:
        command_parts.extend(["-w", p["outfile"]])
    if p["additional_args"]:
        command_parts.append(p["additional_args"])
    if p["domainlist"]:
        command_parts.append(p["domainlist"])
    return " ".join(command_parts)


def _shuffledns_command(p: dict) -> str:
    domain = p["domain"]
    domains = p["domains"]
    if isinstance(domains, str):
        domains = [domains]
    elif not isinstance(domains, list):
        domains = []

    normalized_domains = []
    if isinstance(domain, str) and domain.strip():
        normalized_domains.append(domain.strip())
    for d in domains:
        if isinstance(d, str) and d.strip():
            normalized_domains.append(d.strip())

    mode = p["mode"]
    valid_modes = {"", "bruteforce", "resolve", "filter"}
    if mode not in valid_modes:
        raise ToolValidationError("Invalid mode. Use one of: bruteforce, resolve, filter")

    if not p["update"] and not p["version"]:
        if not normalized_domains and not p["list"] and not p["raw_input"]:
            raise ToolValidationError("Provide at least one input: domain/domains, list, or raw_input")
        if mode == "bruteforce" and not p["wordlist"]:
            raise ToolValidationError("wordlist is required when mode is bruteforce")

    command_parts = ["shuffledns"]
    for d in normalized_domains:
        command_parts.extend(["-d", d])
    if p["auto_domain"]:
        command_parts.append("-ad")
    if p["list"]:
        command_parts.extend(["-l", p["list"]])
    if p["wordlist"]:
        command_parts.extend(["-w", p["wordlist"]])
    if p["resolver"]:
        command_parts.extend(["-r", p["resolver"]])
    if p["trusted_resolver"]:
        command_parts.extend(["-tr", p["trusted_resolver"]])
    if p["raw_input"]:
        command_parts.extend(["-ri", p["raw_input"]])
    if mode:
        command_parts.extend(["-mode", mode])
    if p["threads"]:
        command_parts.extend(["-t", str(p["threads"])])
    if p["output"]:
        command_parts.extend(["-o", p["output"]])
    if p["json"]:
        command_parts.append("-j")
    if p["wildcard_output"]:
        command_parts.extend(["-wo", p["wildcard_output"]])
    if p["massdns"]:
        command_parts.extend(["-m", p["massdns"]])
    if p["massdns_cmd"]:
        command_parts.extend(["-mcmd", p["massdns_cmd"]])
    if p["directory"]:
        command_parts.extend(["-directory", p["directory"]])
    if p["retries"]:
        command_parts.extend(["-retries", str(p["retries"])])
    if p["strict_wildcard"]:
        command_parts.append("-sw")
    if p["wildcard_threads"]:
        command_parts.extend(["-wt", str(p["wildcard_threads"])])
    if p["silent"]:
        command_parts.append("-silent")
    if p["version"]:
        command_parts.append("-version")
    if p["verbose"]:
        command_parts.append("-v")
    if p["no_color"]:
        command_parts.append("-nc")
    if p["update"]:
        command_parts.append("-up")
    if p["disable_update_check"]:
        command_parts.append("-duc")
    if p["additional_args"]:
        command_parts.append(p["additional_args"])
    return " ".join(command_parts)


def _subfinder_command(p: dict) -> str:
    command = f"subfinder -d {p['domain']}"
    if p["silent"]:
        command += " -silent"
    if p["all_sources"]:
        command += " -all"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _theharvester_command(p: dict) -> str:
    return f"theHarvester -d {p['domain']} {p['additional_args']}"


SPECS = [
    ToolSpec(
        name="amass",
        mcp_tool_name="amass_scan",
        endpoint="/api/tools/amass",
        category="recon",
        description="Execute Amass for subdomain enumeration.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain"),
            ParamSpec("mode", str, default="enum", help_text="Amass mode (enum, intel, viz)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Amass arguments"),
        ],
        build_command=_amass_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="assetfinder",
        mcp_tool_name="assetfinder_scan",
        endpoint="/api/tools/assetfinder",
        category="recon",
        description="Execute Assetfinder for passive subdomain enumeration.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain"),
            ParamSpec("only_subdomains", bool, default=True, help_text="Use --subs-only output mode"),
            ParamSpec("additional_args", str, default="", help_text="Additional Assetfinder arguments"),
        ],
        build_command=_assetfinder_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="autorecon",
        mcp_tool_name="autorecon_scan",
        endpoint="/api/tools/autorecon",
        category="recon",
        description="Execute AutoRecon for comprehensive automated reconnaissance.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address or hostname"),
            ParamSpec("output_dir", str, default="/tmp/autorecon", help_text="Output directory for results"),
            ParamSpec("port_scans", str, default="top-100-ports", help_text="Port scan configuration"),
            ParamSpec("service_scans", str, default="default", help_text="Service scan configuration"),
            ParamSpec("heartbeat", int, default=60, help_text="Heartbeat interval in seconds"),
            ParamSpec("timeout", int, default=300, help_text="Timeout for individual scans"),
            ParamSpec("additional_args", str, default="", help_text="Additional AutoRecon arguments"),
        ],
        build_command=_autorecon_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="massdns",
        mcp_tool_name="massdns_scan",
        endpoint="/api/tools/massdns",
        category="recon",
        description="Execute massdns with full CLI flag support for high-performance DNS resolution/bruteforce.",
        params=[
            ParamSpec("domainlist", str, default="", help_text="Path to file containing names to resolve"),
            ParamSpec("bindto", str, default="", help_text="Bind address and port (IP:PORT)"),
            ParamSpec("busy_poll", bool, default=False, help_text="Use busy-wait polling"),
            ParamSpec("resolve_count", int, default=50, help_text="Number of resolves before giving up"),
            ParamSpec("drop_group", str, default="", help_text="Group to drop privileges to"),
            ParamSpec("drop_user", str, default="", help_text="User to drop privileges to"),
            ParamSpec("extended_input", bool, default=False, help_text="Input names include resolver list"),
            ParamSpec("filter", str, default="", help_text="Output only specified response code"),
            ParamSpec("flush", bool, default=False, help_text="Flush output file on each response"),
            ParamSpec("ignore", str, default="", help_text="Exclude specified response code"),
            ParamSpec("interval", int, default=500, help_text="Interval in ms between resolves of same domain"),
            ParamSpec("error_log", str, default="", help_text="Error log path"),
            ParamSpec("norecurse", bool, default=False, help_text="Use non-recursive queries"),
            ParamSpec("output", str, default="", help_text="Output format flags (L,S,F,B,J)"),
            ParamSpec("predictable", bool, default=False, help_text="Use resolvers incrementally"),
            ParamSpec("processes", int, default=1, help_text="Number of resolver processes"),
            ParamSpec("quiet", bool, default=False, help_text="Quiet mode"),
            ParamSpec("rand_src_ipv6", str, default="", help_text="Random IPv6 source subnet"),
            ParamSpec("rcvbuf", int, default=0, help_text="Receive buffer size in bytes"),
            ParamSpec("retry", str, default="", help_text="Unacceptable DNS response codes"),
            ParamSpec("resolvers", str, default="", help_text="Resolver file path"),
            ParamSpec("root", bool, default=False, help_text="Do not drop privileges when running as root"),
            ParamSpec("hashmap_size", int, default=10000, help_text="Number of concurrent lookups"),
            ParamSpec("sndbuf", int, default=0, help_text="Send buffer size in bytes"),
            ParamSpec("status_format", str, default="", help_text="Real-time status format (json, ansi)"),
            ParamSpec("sticky", bool, default=False, help_text="Keep resolver on retry"),
            ParamSpec("socket_count", int, default=1, help_text="Socket count per process"),
            ParamSpec("record_type", str, default="A", help_text="DNS record type (A, AAAA, CNAME, etc.)"),
            ParamSpec("verify_ip", bool, default=False, help_text="Verify IP addresses in incoming replies"),
            ParamSpec("outfile", str, default="", help_text="Output file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional massdns flags"),
        ],
        build_command=_massdns_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="shuffledns",
        mcp_tool_name="shuffledns_scan",
        endpoint="/api/tools/shuffledns",
        category="recon",
        description="Execute shuffleDNS for subdomain bruteforce/resolve/filter with wildcard handling.",
        params=[
            ParamSpec("domain", str, default="", help_text="Single domain target"),
            ParamSpec("domains", list, default=[], help_text="Multiple domain targets"),
            ParamSpec("auto_domain", bool, default=False, help_text="Automatically extract root domains"),
            ParamSpec("list", str, default="", help_text="File containing subdomains to resolve"),
            ParamSpec("wordlist", str, default="", help_text="Wordlist file for bruteforce mode"),
            ParamSpec("resolver", str, default="", help_text="Resolver list file"),
            ParamSpec("trusted_resolver", str, default="", help_text="Trusted resolver list file"),
            ParamSpec("raw_input", str, default="", help_text="Raw massdns output input file"),
            ParamSpec("mode", str, default="", help_text="Execution mode (bruteforce, resolve, filter)"),
            ParamSpec("threads", int, default=10000, help_text="Concurrent massdns resolves"),
            ParamSpec("output", str, default="", help_text="Output file path"),
            ParamSpec("json", bool, default=False, help_text="Output as ndjson"),
            ParamSpec("wildcard_output", str, default="", help_text="Wildcard IP output file"),
            ParamSpec("massdns", str, default="", help_text="Path to massdns binary"),
            ParamSpec("massdns_cmd", str, default="", help_text="Extra massdns commands"),
            ParamSpec("directory", str, default="", help_text="Temporary directory for enumeration"),
            ParamSpec("retries", int, default=5, help_text="Number of retries for DNS enumeration"),
            ParamSpec("strict_wildcard", bool, default=False, help_text="Perform wildcard checks on all found subdomains"),
            ParamSpec("wildcard_threads", int, default=250, help_text="Concurrent wildcard checks"),
            ParamSpec("silent", bool, default=False, help_text="Show only subdomains"),
            ParamSpec("version", bool, default=False, help_text="Show shuffledns version"),
            ParamSpec("verbose", bool, default=False, help_text="Show verbose output"),
            ParamSpec("no_color", bool, default=False, help_text="Disable color output"),
            ParamSpec("update", bool, default=False, help_text="Update shuffledns binary"),
            ParamSpec("disable_update_check", bool, default=False, help_text="Disable auto update check"),
            ParamSpec("additional_args", str, default="", help_text="Additional shuffledns arguments"),
        ],
        build_command=_shuffledns_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="subfinder",
        mcp_tool_name="subfinder_scan",
        endpoint="/api/tools/subfinder",
        category="recon",
        description="Execute Subfinder for passive subdomain enumeration.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain"),
            ParamSpec("silent", bool, default=True, help_text="Run in silent mode"),
            ParamSpec("all_sources", bool, default=False, help_text="Use all sources"),
            ParamSpec("additional_args", str, default="", help_text="Additional Subfinder arguments"),
        ],
        build_command=_subfinder_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="theharvester",
        mcp_tool_name="theharvester_scan",
        endpoint="/api/tools/recon/theharvester",
        category="recon",
        description="Execute TheHarvester for passive information gathering.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain"),
            ParamSpec("additional_args", str, default="", help_text="Additional TheHarvester arguments"),
        ],
        build_command=_theharvester_command,
        use_recovery=True,
    ),
]

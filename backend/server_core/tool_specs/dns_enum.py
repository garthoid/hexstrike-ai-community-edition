import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _fierce_command(p: dict) -> str:
    argv = ["fierce", "--domain", p["domain"]]
    if p["dns_server"]:
        argv.append("--dns-servers")
        argv.append(p["dns_server"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _dnsenum_command(p: dict) -> str:
    argv = ["dnsenum", p["domain"]]
    if p["dns_server"]:
        argv.append("--dnsserver")
        argv.append(p["dns_server"])
    if p["wordlist"]:
        argv.append("--file")
        argv.append(p["wordlist"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="fierce",
        mcp_tool_name="fierce_scan",
        endpoint="/api/tools/fierce",
        category="dns_enum",
        description="Execute fierce for DNS reconnaissance with enhanced logging.",
        params=[
            ParamSpec("domain", str, required=True, help_text="Target domain"),
            ParamSpec("dns_server", str, default="", help_text="DNS server to use"),
            ParamSpec("additional_args", str, default="", help_text="Additional fierce arguments"),
        ],
        build_command=_fierce_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="dnsenum",
        mcp_tool_name="dnsenum_scan",
        endpoint="/api/tools/dnsenum",
        category="dns_enum",
        description="Execute dnsenum for DNS enumeration with enhanced logging.",
        params=[
            ParamSpec("domain", str, required=True, help_text="Target domain"),
            ParamSpec("dns_server", str, default="", help_text="DNS server to use"),
            ParamSpec("wordlist", str, default="", help_text="Wordlist for brute forcing"),
            ParamSpec("additional_args", str, default="", help_text="Additional dnsenum arguments"),
        ],
        build_command=_dnsenum_command,
        use_recovery=True,
    ),
]

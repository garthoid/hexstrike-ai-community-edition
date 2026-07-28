from server_core.tool_spec import ParamSpec, ToolSpec


def _nbtscan_command(p: dict) -> str:
    command = f"nbtscan -t {p['timeout']}"
    if p["verbose"]:
        command += " -v"
    command += f" {p['target']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _enum4linux_command(p: dict) -> str:
    return f"enum4linux {p['additional_args']} {p['target']}"


def _enum4linux_ng_command(p: dict) -> str:
    command = f"enum4linux-ng {p['target']}"
    if p["username"]:
        command += f" -u {p['username']}"
    if p["password"]:
        command += f" -p {p['password']}"
    if p["domain"]:
        command += f" -d {p['domain']}"

    enum_options = []
    if p["shares"]:
        enum_options.append("S")
    if p["users"]:
        enum_options.append("U")
    if p["groups"]:
        enum_options.append("G")
    if p["policy"]:
        enum_options.append("P")
    if enum_options:
        command += f" -A {','.join(enum_options)}"

    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _netexec_command(p: dict) -> str:
    command = f"nxc {p['protocol']} {p['target']}"
    if p["username"]:
        command += f" -u {p['username']}"
    if p["password"]:
        command += f" -p {p['password']}"
    if p["hash"]:
        command += f" -H {p['hash']}"
    if p["module"]:
        command += f" -M {p['module']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _smbmap_command(p: dict) -> str:
    command = f"smbmap -H {p['target']}"
    if p["username"]:
        command += f" -u {p['username']}"
    if p["password"]:
        command += f" -p {p['password']}"
    if p["domain"]:
        command += f" -d {p['domain']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _rpcclient_command(p: dict) -> str:
    if p["username"] and p["password"]:
        auth_string = f"-U {p['username']}%{p['password']}"
    elif p["username"]:
        auth_string = f"-U {p['username']}"
    else:
        auth_string = "-U ''"

    if p["domain"]:
        auth_string += f" -W {p['domain']}"

    command_sequence = p["commands"].replace(";", "\n")
    command = f"echo -e '{command_sequence}' | rpcclient {auth_string} {p['target']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


SPECS = [
    ToolSpec(
        name="nbtscan",
        mcp_tool_name="nbtscan_netbios",
        endpoint="/api/tools/nbtscan",
        category="smb_enum",
        description="Execute nbtscan for NetBIOS name scanning.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address or range"),
            ParamSpec("verbose", bool, default=False, help_text="Enable verbose output"),
            ParamSpec("timeout", int, default=2, help_text="Timeout in seconds"),
            ParamSpec("additional_args", str, default="", help_text="Additional nbtscan arguments"),
        ],
        build_command=_nbtscan_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="enum4linux",
        mcp_tool_name="enum4linux_scan",
        endpoint="/api/tools/enum4linux",
        category="smb_enum",
        description="Execute Enum4linux for SMB enumeration.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address"),
            ParamSpec("additional_args", str, default="-a", help_text="Additional Enum4linux arguments"),
        ],
        build_command=_enum4linux_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="enum4linux-ng",
        mcp_tool_name="enum4linux_ng_advanced",
        endpoint="/api/tools/enum4linux-ng",
        category="smb_enum",
        description="Execute Enum4linux-ng for advanced SMB enumeration.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address"),
            ParamSpec("username", str, default="", help_text="Username for authentication"),
            ParamSpec("password", str, default="", help_text="Password for authentication"),
            ParamSpec("domain", str, default="", help_text="Domain for authentication"),
            ParamSpec("shares", bool, default=True, help_text="Enumerate shares"),
            ParamSpec("users", bool, default=True, help_text="Enumerate users"),
            ParamSpec("groups", bool, default=True, help_text="Enumerate groups"),
            ParamSpec("policy", bool, default=True, help_text="Enumerate policies"),
            ParamSpec("additional_args", str, default="", help_text="Additional Enum4linux-ng arguments"),
        ],
        build_command=_enum4linux_ng_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="netexec",
        mcp_tool_name="netexec_scan",
        endpoint="/api/tools/netexec",
        category="smb_enum",
        description="Execute NetExec (formerly CrackMapExec) for network enumeration.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP or network"),
            ParamSpec("protocol", str, default="smb", help_text="Protocol to use (smb, ssh, winrm, etc.)"),
            ParamSpec("username", str, default="", help_text="Username for authentication"),
            ParamSpec("password", str, default="", help_text="Password for authentication"),
            ParamSpec("hash", str, default="", help_text="Hash for pass-the-hash attacks"),
            ParamSpec("module", str, default="", help_text="NetExec module to execute"),
            ParamSpec("additional_args", str, default="", help_text="Additional NetExec arguments"),
        ],
        build_command=_netexec_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="smbmap",
        mcp_tool_name="smbmap_scan",
        endpoint="/api/tools/smbmap",
        category="smb_enum",
        description="Execute SMBMap for SMB share enumeration.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address"),
            ParamSpec("username", str, default="", help_text="Username for authentication"),
            ParamSpec("password", str, default="", help_text="Password for authentication"),
            ParamSpec("domain", str, default="", help_text="Domain for authentication"),
            ParamSpec("additional_args", str, default="", help_text="Additional SMBMap arguments"),
        ],
        build_command=_smbmap_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="rpcclient",
        mcp_tool_name="rpcclient_enumeration",
        endpoint="/api/tools/rpcclient",
        category="smb_enum",
        description="Execute rpcclient for RPC enumeration.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP address"),
            ParamSpec("username", str, default="", help_text="Username for authentication"),
            ParamSpec("password", str, default="", help_text="Password for authentication"),
            ParamSpec("domain", str, default="", help_text="Domain for authentication"),
            ParamSpec("commands", str, default="enumdomusers;enumdomgroups;querydominfo", help_text="Semicolon-separated RPC commands"),
            ParamSpec("additional_args", str, default="", help_text="Additional rpcclient arguments"),
        ],
        build_command=_rpcclient_command,
        use_recovery=True,
    ),
]

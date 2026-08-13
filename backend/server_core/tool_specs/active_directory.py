import shlex

from backend.server_core.impacket_helpers import (
    IMPACKET_SCRIPTS,
    _build_impacket_command,
    get_impacket_script_spec,
)
from backend.server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _ldapdomaindump_build_command(p: dict) -> str:
    cmd = ["ldapdomaindump", p["hostname"], "--authtype", p["authtype"]]
    if p["username"] and p["password"]:
        cmd.extend(["--user", p["username"], "--password", p["password"]])
    return shlex.join(cmd)


def _impacket_run_build_command(p: dict) -> str:
    script_name = p["script"].strip()

    if not script_name:
        raise ToolValidationError("script parameter is required")

    if script_name not in IMPACKET_SCRIPTS:
        raise ToolValidationError(
            f"Unsupported Impacket script: {script_name}",
            supported_scripts=sorted(IMPACKET_SCRIPTS),
        )

    options = {}
    options.update(p.get("options") or {})
    options.update(p.get("extra_options") or {})
    if p.get("dc_ip"):
        options["dc-ip"] = p["dc_ip"]
    if p.get("hashes"):
        options["hashes"] = p["hashes"]
    if p.get("kerberos"):
        options["k"] = True
    if p.get("no_pass"):
        options["no-pass"] = True
    if p.get("aes_key"):
        options["aesKey"] = p["aes_key"]
    if p.get("debug"):
        options["debug"] = True
    if p.get("share"):
        options["share"] = p["share"]
    if p.get("shell_type"):
        options["shell-type"] = p["shell_type"]
    if p.get("command"):
        options["command"] = p["command"]
    if p.get("username"):
        options.setdefault("username", p["username"])
    if p.get("password"):
        options.setdefault("password", p["password"])

    payload = dict(p)
    payload["options"] = options

    try:
        argv, _spec = _build_impacket_command(script_name, payload)
    except ValueError as e:
        raise ToolValidationError(str(e)) from e

    return shlex.join(argv)


def _impacket_get_spec_handler(p: dict) -> dict:
    script_name = p["script"].strip()

    try:
        spec = get_impacket_script_spec(script_name)
    except Exception as e:
        raise ToolValidationError(str(e)) from e

    return {
        "script": spec["script"],
        "binary": spec["binary"],
        "usage": spec["usage"],
        "required_positionals": spec["required_positionals"],
        "options": spec["options"],
    }


def _impacket_run_postprocess(raw: dict, p: dict) -> dict:
    spec = get_impacket_script_spec(p["script"].strip())

    if isinstance(raw, dict):
        raw.setdefault("meta", {})
        raw["meta"]["script"] = spec["script"]
        raw["meta"]["binary"] = spec["binary"]
        raw["meta"]["usage"] = spec["usage"]
        raw["meta"]["required_positionals"] = spec["required_positionals"]

    return raw


SPECS = [
    ToolSpec(
        name="ldapdomaindump",
        mcp_tool_name="ldapdomaindump",
        endpoint="/api/tools/active_directory/ldapdomaindump",
        category="active_directory",
        description="Run the ldapdomaindump tool to enumerate and dump Active Directory domain information via LDAP.",
        params=[
            ParamSpec("hostname", str, required=True, help_text="Target LDAP/domain controller hostname or IP"),
            ParamSpec("username", str, default="", help_text="Bind username (leave blank for anonymous bind)"),
            ParamSpec("password", str, default="", help_text="Bind password"),
            ParamSpec("authtype", str, default="NTLM", help_text="Authentication type (e.g. NTLM, SIMPLE)"),
        ],
        build_command=_ldapdomaindump_build_command,
    ),
    ToolSpec(
        name="impacket_run",
        mcp_tool_name="impacket_run",
        endpoint="/api/tool/active_directory/impacket",
        category="active_directory",
        description=(
            "Execute any supported Impacket script through the generic backend wrapper "
            "(e.g. GetADUsers, GetNPUsers, psexec, smbclient)."
        ),
        params=[
            ParamSpec(
                "script", str, required=True,
                help_text="Impacket script name without the 'impacket-' prefix (e.g. GetADUsers, GetNPUsers, psexec, smbclient)",
            ),
            ParamSpec("target", str, default="", help_text="Primary target/credential string for scripts that require it"),
            ParamSpec(
                "options", dict, default={},
                help_text='Dictionary of script flags/options, e.g. {"dc-ip": "10.10.10.10", "all": true, "debug": true}',
            ),
            ParamSpec("positional", list, default=[], help_text="Extra positional arguments as a list, e.g. ['input.kirbi', 'output.ccache']"),
            ParamSpec("positional_map", dict, default={}, help_text="Named positional arguments if the script supports them"),
            ParamSpec("extra_args", str, default="", help_text="Raw extra CLI args for edge cases"),
            ParamSpec("extra_options", dict, default={}, help_text="Base dict of script flags/options, merged under 'options'"),
            ParamSpec("dc_ip", str, default="", help_text="Domain controller IP (shortcut for options['dc-ip'])"),
            ParamSpec("username", str, default="", help_text="Username (shortcut for options['username'])"),
            ParamSpec("password", str, default="", help_text="Password (shortcut for options['password'])"),
            ParamSpec("hashes", str, default="", help_text="LM:NT hashes (shortcut for options['hashes'])"),
            ParamSpec("kerberos", bool, default=False, help_text="Enable Kerberos auth (shortcut for options['k'])"),
            ParamSpec("no_pass", bool, default=False, help_text="Enable -no-pass (shortcut for options['no-pass'])"),
            ParamSpec("aes_key", str, default="", help_text="AES key for Kerberos auth (shortcut for options['aesKey'])"),
            ParamSpec("debug", bool, default=False, help_text="Enable -debug (shortcut for options['debug'])"),
            ParamSpec("share", str, default="", help_text="SMB share if supported (shortcut for options['share'])"),
            ParamSpec("shell_type", str, default="", help_text="Shell type if supported (shortcut for options['shell-type'])"),
            ParamSpec("command", str, default="", help_text="Command to execute if supported by the script (shortcut for options['command'])"),
        ],
        build_command=_impacket_run_build_command,
        postprocess=_impacket_run_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="impacket_get_spec",
        mcp_tool_name="impacket_get_spec",
        endpoint="/api/tool/active_directory/impacket/spec",
        category="active_directory",
        description=(
            "Fetch the backend-discovered specification for an Impacket script — required "
            "positional arguments, supported options, and usage string. Useful for agents/UI "
            "logic to discover a script's interface before calling impacket_run."
        ),
        params=[
            ParamSpec("script", str, required=True, help_text="Impacket script name without the 'impacket-' prefix"),
        ],
        handler=_impacket_get_spec_handler,
    ),
    ToolSpec(
        name="impacket_ad_enum",
        mcp_tool_name="impacket_ad_enum",
        endpoint="/api/tool/active_directory/impacket/ad-enum",
        category="active_directory",
        description=(
            "Convenience wrapper for common AD enumeration Impacket scripts: GetADUsers, "
            "GetADComputers, GetNPUsers, GetUserSPNs, GetLAPSPassword, findDelegation, lookupsid."
        ),
        params=[
            ParamSpec("script", str, required=True, help_text="Script name without 'impacket-' prefix"),
            ParamSpec("target", str, required=True, help_text="Target string expected by the script"),
            ParamSpec("dc_ip", str, default="", help_text="Domain controller IP"),
            ParamSpec("username", str, default="", help_text="Optional username for scripts/agent formatting"),
            ParamSpec("password", str, default="", help_text="Optional password for scripts/agent formatting"),
            ParamSpec("hashes", str, default="", help_text="LM:NT hashes"),
            ParamSpec("kerberos", bool, default=False, help_text="Enable -k"),
            ParamSpec("no_pass", bool, default=False, help_text="Enable -no-pass"),
            ParamSpec("aes_key", str, default="", help_text="AES key for Kerberos auth"),
            ParamSpec("debug", bool, default=False, help_text="Enable -debug"),
            ParamSpec("extra_options", dict, default={}, help_text="Extra options dict merged into generated options"),
            ParamSpec("extra_args", str, default="", help_text="Raw extra CLI args for edge cases"),
        ],
        build_command=_impacket_run_build_command,
        postprocess=_impacket_run_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="impacket_remote_exec",
        mcp_tool_name="impacket_remote_exec",
        endpoint="/api/tool/active_directory/impacket/remote-exec",
        category="active_directory",
        description=(
            "Convenience wrapper for remote execution / interaction style scripts: psexec, "
            "smbexec, wmiexec, dcomexec, atexec, smbclient."
        ),
        params=[
            ParamSpec("script", str, required=True, help_text="Script name without 'impacket-' prefix"),
            ParamSpec("target", str, required=True, help_text="Full target string"),
            ParamSpec("command", str, default="", help_text="Optional command to execute if supported by the script"),
            ParamSpec("username", str, default="", help_text="Username for authentication"),
            ParamSpec("password", str, default="", help_text="Password for authentication"),
            ParamSpec("hashes", str, default="", help_text="LM:NT hashes"),
            ParamSpec("kerberos", bool, default=False, help_text="Enable -k"),
            ParamSpec("no_pass", bool, default=False, help_text="Enable -no-pass"),
            ParamSpec("aes_key", str, default="", help_text="AES key for Kerberos auth"),
            ParamSpec("share", str, default="", help_text="SMB share if supported"),
            ParamSpec("shell_type", str, default="", help_text="Shell type if supported"),
            ParamSpec("debug", bool, default=False, help_text="Enable -debug"),
            ParamSpec("extra_options", dict, default={}, help_text="Additional options"),
            ParamSpec("extra_args", str, default="", help_text="Raw fallback args"),
        ],
        build_command=_impacket_run_build_command,
        postprocess=_impacket_run_postprocess,
        use_recovery=True,
    ),
]

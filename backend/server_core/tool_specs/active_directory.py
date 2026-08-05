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

    try:
        argv, _spec = _build_impacket_command(script_name, p)
    except ValueError as e:
        raise ToolValidationError(str(e)) from e

    return shlex.join(argv)


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
        ],
        build_command=_impacket_run_build_command,
        postprocess=_impacket_run_postprocess,
        use_recovery=True,
    ),
]

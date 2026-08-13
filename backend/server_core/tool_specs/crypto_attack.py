import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _hashpump_command(p: dict) -> str:
    argv = ["hashpump", "-s", p["signature"], "-d", p["data"], "-k", p["key_length"], "-a", p["append_data"]]
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="hashpump",
        mcp_tool_name="hashpump_attack",
        endpoint="/api/tools/hashpump",
        category="crypto_attack",
        description="Execute HashPump for hash length extension attacks with enhanced logging.",
        params=[
            ParamSpec("signature", str, required=True, help_text="Original hash signature"),
            ParamSpec("data", str, required=True, help_text="Original data"),
            ParamSpec("key_length", str, required=True, help_text="Length of secret key"),
            ParamSpec("append_data", str, required=True, help_text="Data to append"),
            ParamSpec("additional_args", str, default="", help_text="Additional HashPump arguments"),
        ],
        build_command=_hashpump_command,
    ),
]

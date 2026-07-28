from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _steghide_command(p: dict) -> str:
    action = p["action"]
    cover_file = p["cover_file"]

    if action == "extract":
        command = f"steghide extract -sf {cover_file}"
        if p["output_file"]:
            command += f" -xf {p['output_file']}"
    elif action == "embed":
        if not p["embed_file"]:
            raise ToolValidationError("Embed file required for embed action")
        command = f"steghide embed -cf {cover_file} -ef {p['embed_file']}"
    elif action == "info":
        command = f"steghide info {cover_file}"
    else:
        raise ToolValidationError("Invalid action. Use: extract, embed, info")

    if p["passphrase"]:
        command += f" -p {p['passphrase']}"
    else:
        command += " -p ''"

    if p["additional_args"]:
        command += f" {p['additional_args']}"

    return command


SPECS = [
    ToolSpec(
        name="steghide",
        mcp_tool_name="steghide_analysis",
        endpoint="/api/tools/steghide",
        category="stego_analysis",
        description="Execute Steghide for steganography analysis.",
        params=[
            ParamSpec("cover_file", str, required=True, help_text="Cover file for steganography"),
            ParamSpec("action", str, default="extract", help_text="Action to perform (extract, embed, info)"),
            ParamSpec("embed_file", str, default="", help_text="File to embed (for embed action)"),
            ParamSpec("passphrase", str, default="", help_text="Passphrase for steganography"),
            ParamSpec("output_file", str, default="", help_text="Output file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional Steghide arguments"),
        ],
        build_command=_steghide_command,
        use_recovery=True,
    ),
]

from server_core.tool_spec import ParamSpec, ToolSpec


def _exiftool_command(p: dict) -> str:
    command = "exiftool"
    if p["output_format"]:
        command += f" -{p['output_format']}"
    if p["tags"]:
        command += f" -{p['tags']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += f" {p['file_path']}"
    return command


SPECS = [
    ToolSpec(
        name="exiftool",
        mcp_tool_name="exiftool_extract",
        endpoint="/api/tools/exiftool",
        category="metadata_extract",
        description="Execute ExifTool for metadata extraction with enhanced logging.",
        params=[
            ParamSpec("file_path", str, required=True, help_text="Path to file for metadata extraction"),
            ParamSpec("output_format", str, default="", help_text="Output format (json, xml, csv)"),
            ParamSpec("tags", str, default="", help_text="Specific tags to extract"),
            ParamSpec("additional_args", str, default="", help_text="Additional ExifTool arguments"),
        ],
        build_command=_exiftool_command,
        use_recovery=True,
    ),
]

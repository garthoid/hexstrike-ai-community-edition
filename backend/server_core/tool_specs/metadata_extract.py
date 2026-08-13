import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _exiftool_command(p: dict) -> str:
    argv = ["exiftool"]
    if p["output_format"]:
        argv.append(f"-{p['output_format']}")
    if p["tags"]:
        argv.append(f"-{p['tags']}")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    argv.append(p["file_path"])
    return shlex.join(argv)


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

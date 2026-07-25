from pathlib import Path

from server_core.tool_spec import ParamSpec, ToolSpec


def _foremost_command(p: dict) -> str:
    Path(p["output_dir"]).mkdir(parents=True, exist_ok=True)

    command = f"foremost -o {p['output_dir']}"
    if p["file_types"]:
        command += f" -t {p['file_types']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += f" {p['input_file']}"
    return command


def _foremost_postprocess(raw: dict, p: dict) -> dict:
    raw["output_directory"] = p["output_dir"]
    return raw


SPECS = [
    ToolSpec(
        name="foremost",
        mcp_tool_name="foremost_carving",
        endpoint="/api/tools/foremost",
        category="file_carving",
        description="Execute Foremost for file carving with enhanced logging.",
        params=[
            ParamSpec("input_file", str, required=True, help_text="Input file or device to carve"),
            ParamSpec("output_dir", str, default="/tmp/foremost_output", help_text="Output directory for carved files"),
            ParamSpec("file_types", str, default="", help_text="File types to carve (jpg,gif,png,etc.)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Foremost arguments"),
        ],
        build_command=_foremost_command,
        postprocess=_foremost_postprocess,
        use_recovery=True,
    ),
]

import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _qsreplace_command(p: dict) -> str:
    echo_argv = ["echo", p["urls"]]
    qsreplace_argv = ["qsreplace", p["replacement"]]
    if p["additional_args"]:
        qsreplace_argv += shlex.split(p["additional_args"])
    return shlex.join(echo_argv) + " | " + shlex.join(qsreplace_argv)


SPECS = [
    ToolSpec(
        name="qsreplace",
        mcp_tool_name="qsreplace_parameter_replacement",
        endpoint="/api/tools/qsreplace",
        category="param_fuzz",
        description="Execute qsreplace for query string parameter replacement.",
        params=[
            ParamSpec("urls", str, required=True, help_text="URLs to process"),
            ParamSpec("replacement", str, default="FUZZ", help_text="Replacement string for parameters"),
            ParamSpec("additional_args", str, default="", help_text="Additional qsreplace arguments"),
        ],
        build_command=_qsreplace_command,
        use_recovery=True,
    ),
]

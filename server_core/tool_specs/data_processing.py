import shlex
import shutil

from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError

_HURL_MODE_FLAGS = {
    "base64_encode": "-B",
    "base64_decode": "-b",
    "url_encode": "-U",
    "url_decode": "-u",
    "double_url_encode": "-D",
    "double_url_decode": "-d",
    "html_encode": "-H",
    "html_decode": "-h",
    "hex_encode": "-X",
    "hex_decode": "-x",
    "sha1": "-2",
    "sha256": "-4",
    "sha512": "-6",
    "md5": "-m",
    "rot13_encode": "-7",
    "rot13_decode": "-8",
}


def _anew_command(p: dict) -> str:
    echo_argv = ["echo", p["input_data"]]
    anew_argv = ["anew"]
    if p["output_file"]:
        anew_argv.append(p["output_file"])
    if p["additional_args"]:
        anew_argv += shlex.split(p["additional_args"])
    return shlex.join(echo_argv) + " | " + shlex.join(anew_argv)


def _hurl_command(p: dict) -> str:
    mode = p["mode"]
    if mode not in _HURL_MODE_FLAGS:
        raise ToolValidationError("Invalid mode", valid_modes=sorted(_HURL_MODE_FLAGS.keys()))

    hurl_executable = shutil.which("hURL") or shutil.which("hurl")
    if not hurl_executable:
        raise ToolValidationError("hURL tool not found", install_hint="sudo apt install hurl")

    args = [hurl_executable, _HURL_MODE_FLAGS[mode]]
    if p["suppress"]:
        args.append("-s")
    if p["additional_args"]:
        args.extend(shlex.split(p["additional_args"]))
    args.append(p["input"])
    return " ".join(shlex.quote(arg) for arg in args)


SPECS = [
    ToolSpec(
        name="anew",
        mcp_tool_name="anew_data_processing",
        endpoint="/api/tools/anew",
        category="data_processing",
        description="Execute anew for appending new lines to files (useful for data processing).",
        params=[
            ParamSpec("input_data", str, required=True, help_text="Input data to process"),
            ParamSpec("output_file", str, default="", help_text="Output file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional anew arguments"),
        ],
        build_command=_anew_command,
    ),
    ToolSpec(
        name="hurl",
        mcp_tool_name="hurl_request",
        endpoint="/api/tools/data_processing/hurl",
        category="data_processing",
        description="Execute hURL for string encoding, decoding, and hashing transformations.",
        params=[
            ParamSpec("input", str, required=True, help_text="Input string value to transform"),
            ParamSpec("mode", str, default="base64_encode", help_text="Transformation mode"),
            ParamSpec("suppress", bool, default=True, help_text="Return result only by adding -s"),
            ParamSpec("additional_args", str, default="", help_text="Additional hURL arguments"),
        ],
        build_command=_hurl_command,
        use_cache=False,
    ),
]

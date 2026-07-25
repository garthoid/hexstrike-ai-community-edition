import os

from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _cleanup_tmp_script_postprocess(raw, params: dict):
    tmp_script = params.pop("_tmp_script", None)
    if tmp_script and os.path.exists(tmp_script):
        try:
            os.remove(tmp_script)
        except OSError:
            pass
    return raw


def _gdb_command(p: dict) -> str:
    command = f"gdb {p['binary']}"
    if p["script_file"]:
        command += f" -x {p['script_file']}"
    if p["commands"]:
        temp_script = "/tmp/gdb_commands.txt"
        with open(temp_script, "w") as f:
            f.write(p["commands"])
        command += f" -x {temp_script}"
        p["_tmp_script"] = temp_script
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += " -batch"
    return command


def _gdb_peda_command(p: dict) -> str:
    binary, attach_pid, core_file = p["binary"], p["attach_pid"], p["core_file"]
    if not binary and not attach_pid and not core_file:
        raise ToolValidationError("Binary, PID, or core file parameter is required")

    command = "gdb -q"
    if binary:
        command += f" {binary}"
    if core_file:
        command += f" {core_file}"
    if attach_pid:
        command += f" -p {attach_pid}"

    if p["commands"]:
        temp_script = "/tmp/gdb_peda_commands.txt"
        peda_commands = f"\nsource ~/peda/peda.py\n{p['commands']}\nquit\n"
        with open(temp_script, "w") as f:
            f.write(peda_commands)
        command += f" -x {temp_script}"
        p["_tmp_script"] = temp_script
    else:
        command += " -ex 'source ~/peda/peda.py' -ex 'quit'"

    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _radare2_command(p: dict) -> str:
    binary = p["binary"]
    if p["commands"]:
        temp_script = "/tmp/r2_commands.txt"
        with open(temp_script, "w") as f:
            f.write(p["commands"])
        command = f"r2 -i {temp_script} -q {binary}"
        p["_tmp_script"] = temp_script
    else:
        command = f"r2 -q {binary}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


SPECS = [
    ToolSpec(
        name="gdb",
        mcp_tool_name="gdb_analyze",
        endpoint="/api/tools/gdb",
        category="binary_debug",
        description="Execute GDB for binary analysis and debugging.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Path to the binary file"),
            ParamSpec("commands", str, default="", help_text="GDB commands to execute"),
            ParamSpec("script_file", str, default="", help_text="Path to GDB script file"),
            ParamSpec("additional_args", str, default="", help_text="Additional GDB arguments"),
        ],
        build_command=_gdb_command,
        postprocess=_cleanup_tmp_script_postprocess,
    ),
    ToolSpec(
        name="gdb-peda",
        mcp_tool_name="gdb_peda_debug",
        endpoint="/api/tools/gdb-peda",
        category="binary_debug",
        description="Execute GDB with PEDA for enhanced debugging and exploitation.",
        params=[
            ParamSpec("binary", str, default="", help_text="Binary to debug"),
            ParamSpec("commands", str, default="", help_text="GDB commands to execute"),
            ParamSpec("attach_pid", int, default=0, help_text="Process ID to attach to"),
            ParamSpec("core_file", str, default="", help_text="Core dump file to analyze"),
            ParamSpec("additional_args", str, default="", help_text="Additional GDB arguments"),
        ],
        build_command=_gdb_peda_command,
        postprocess=_cleanup_tmp_script_postprocess,
    ),
    ToolSpec(
        name="radare2",
        mcp_tool_name="radare2_analyze",
        endpoint="/api/tools/radare2",
        category="binary_debug",
        description="Execute Radare2 for binary analysis and reverse engineering.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Path to the binary file"),
            ParamSpec("commands", str, default="", help_text="Radare2 commands to execute"),
            ParamSpec("additional_args", str, default="", help_text="Additional Radare2 arguments"),
        ],
        build_command=_radare2_command,
        postprocess=_cleanup_tmp_script_postprocess,
    ),
]

import os

from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError

_ANGR_SCRIPT = "/tmp/angr_analysis.py"


def _angr_command(p: dict) -> str:
    binary = p["binary"]
    script_content = p["script_content"]
    find_address = p["find_address"]
    avoid_addresses = p["avoid_addresses"]
    analysis_type = p["analysis_type"]

    if script_content:
        content = script_content
    else:
        template = f"""#!/usr/bin/env python3
import angr
import sys

# Load binary
project = angr.Project('{binary}', auto_load_libs=False)
print(f"Loaded binary: {binary}")
print(f"Architecture: {{project.arch}}")
print(f"Entry point: {{hex(project.entry)}}")

"""
        if analysis_type == "symbolic":
            template += f"""
# Symbolic execution
state = project.factory.entry_state()
simgr = project.factory.simulation_manager(state)

# Find and avoid addresses
find_addr = {find_address if find_address else 'None'}
avoid_addrs = {avoid_addresses.split(',') if avoid_addresses else '[]'}

if find_addr:
    simgr.explore(find=find_addr, avoid=avoid_addrs)
    if simgr.found:
        print("Found solution!")
        solution_state = simgr.found[0]
        print(f"Input: {{solution_state.posix.dumps(0)}}")
    else:
        print("No solution found")
else:
    print("No find address specified, running basic analysis")
"""
        elif analysis_type == "cfg":
            template += """
# Control Flow Graph analysis
cfg = project.analyses.CFGFast()
print(f"CFG nodes: {len(cfg.graph.nodes())}")
print(f"CFG edges: {len(cfg.graph.edges())}")

# Function analysis
for func_addr, func in cfg.functions.items():
    print(f"Function: {func.name} at {hex(func_addr)}")
"""
        content = template

    with open(_ANGR_SCRIPT, "w") as f:
        f.write(content)

    command = f"python3 {_ANGR_SCRIPT}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _angr_cleanup_postprocess(raw, params: dict):
    try:
        os.remove(_ANGR_SCRIPT)
    except Exception:
        pass
    return raw


def _autopsy_command(p: dict) -> str:
    return "autopsy &"


def _binwalk_command(p: dict) -> str:
    command = "binwalk"
    if p["extract"]:
        command += " -e"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += f" {p['file_path']}"
    return command


def _checksec_command(p: dict) -> str:
    return f"checksec --file={p['binary']}"


def _ghidra_command(p: dict) -> str:
    project_name = p["project_name"]
    project_dir = f"/tmp/ghidra_projects/{project_name}"
    os.makedirs(project_dir, exist_ok=True)

    command = f"analyzeHeadless {project_dir} {project_name} -import {p['binary']} -deleteProject"
    if p["script_file"]:
        command += f" -postScript {p['script_file']}"
    if p["output_format"] == "xml":
        command += f" -postScript ExportXml.java {project_dir}/analysis.xml"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _one_gadget_command(p: dict) -> str:
    command = f"one_gadget {p['libc_path']} --level {p['level']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _ropper_command(p: dict) -> str:
    command = f"ropper --file {p['binary']}"
    gadget_type = p["gadget_type"]
    if gadget_type == "rop":
        command += " --rop"
    elif gadget_type == "jop":
        command += " --jop"
    elif gadget_type == "sys":
        command += " --sys"
    elif gadget_type == "all":
        command += " --all"
    if p["quality"] > 1:
        command += f" --quality {p['quality']}"
    if p["arch"]:
        command += f" --arch {p['arch']}"
    if p["search_string"]:
        command += f" --search '{p['search_string']}'"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _libc_database_command(p: dict) -> str:
    action, symbols, libc_id = p["action"], p["symbols"], p["libc_id"]
    if action == "find" and not symbols:
        raise ToolValidationError("Symbols parameter is required for find action")
    if action in ("dump", "download") and not libc_id:
        raise ToolValidationError("libc_id parameter is required for dump/download actions")

    base_command = "cd /opt/libc-database 2>/dev/null || cd ~/libc-database 2>/dev/null || echo 'libc-database not found'"

    if action == "find":
        command = f"{base_command} && ./find {symbols}"
    elif action == "dump":
        command = f"{base_command} && ./dump {libc_id}"
    elif action == "download":
        command = f"{base_command} && ./download {libc_id}"
    else:
        raise ToolValidationError(f"Invalid action: {action}")

    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _objdump_command(p: dict) -> str:
    command = "objdump"
    command += " -d" if p["disassemble"] else " -x"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += f" {p['binary']}"
    return command


def _strings_command(p: dict) -> str:
    command = f"strings -n {p['min_len']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += f" {p['file_path']}"
    return command


def _xxd_command(p: dict) -> str:
    command = f"xxd -s {p['offset']}"
    if p["length"]:
        command += f" -l {p['length']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    command += f" {p['file_path']}"
    return command


SPECS = [
    ToolSpec(
        name="angr",
        mcp_tool_name="angr_symbolic_execution",
        endpoint="/api/tools/angr",
        category="binary_analysis",
        description="Execute angr for symbolic execution and binary analysis.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Binary to analyze"),
            ParamSpec("script_content", str, default="", help_text="Custom angr script content"),
            ParamSpec("find_address", str, default="", help_text="Address to find during symbolic execution"),
            ParamSpec("avoid_addresses", str, default="", help_text="Comma-separated addresses to avoid"),
            ParamSpec("analysis_type", str, default="symbolic", help_text="Type of analysis (symbolic, cfg, static)"),
            ParamSpec("additional_args", str, default="", help_text="Additional arguments"),
        ],
        build_command=_angr_command,
        postprocess=_angr_cleanup_postprocess,
        timeout=600,
        use_recovery=True,
    ),
    ToolSpec(
        name="autopsy",
        mcp_tool_name="autopsy_analysis",
        endpoint="/api/tools/binary_analysis/autopsy",
        category="binary_analysis",
        description="Launch the Autopsy digital forensics web server and provide access instructions.",
        params=[],
        build_command=_autopsy_command,
        use_cache=False,
        use_recovery=True,
    ),
    ToolSpec(
        name="binwalk",
        mcp_tool_name="binwalk_analyze",
        endpoint="/api/tools/binwalk",
        category="binary_analysis",
        description="Execute Binwalk for firmware and file analysis.",
        params=[
            ParamSpec("file_path", str, required=True, help_text="Path to the file to analyze"),
            ParamSpec("extract", bool, default=False, help_text="Whether to extract discovered files"),
            ParamSpec("additional_args", str, default="", help_text="Additional Binwalk arguments"),
        ],
        build_command=_binwalk_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="checksec",
        mcp_tool_name="checksec_analyze",
        endpoint="/api/tools/checksec",
        category="binary_analysis",
        description="Check security features of a binary.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Path to the binary file"),
        ],
        build_command=_checksec_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="ghidra",
        mcp_tool_name="ghidra_analysis",
        endpoint="/api/tools/ghidra",
        category="binary_analysis",
        description="Execute Ghidra for advanced binary analysis and reverse engineering.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Path to the binary file"),
            ParamSpec("project_name", str, default="analysis_project", help_text="Ghidra project name"),
            ParamSpec("script_file", str, default="", help_text="Custom Ghidra script to run"),
            ParamSpec("analysis_timeout", int, default=300, help_text="Analysis timeout in seconds"),
            ParamSpec("output_format", str, default="xml", help_text="Output format (xml, json)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Ghidra arguments"),
        ],
        build_command=_ghidra_command,
        timeout_param="analysis_timeout",
        use_recovery=True,
    ),
    ToolSpec(
        name="one-gadget",
        mcp_tool_name="one_gadget_search",
        endpoint="/api/tools/one-gadget",
        category="binary_analysis",
        description="Execute one_gadget to find one-shot RCE gadgets in libc.",
        params=[
            ParamSpec("libc_path", str, required=True, help_text="Path to libc binary"),
            ParamSpec("level", int, default=1, help_text="Constraint level (0, 1, 2)"),
            ParamSpec("additional_args", str, default="", help_text="Additional one_gadget arguments"),
        ],
        build_command=_one_gadget_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="ropper",
        mcp_tool_name="ropper_gadget_search",
        endpoint="/api/tools/ropper",
        category="binary_analysis",
        description="Execute ropper for advanced ROP/JOP gadget searching.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Binary to search for gadgets"),
            ParamSpec("gadget_type", str, default="rop", help_text="Type of gadgets (rop, jop, sys, all)"),
            ParamSpec("quality", int, default=1, help_text="Gadget quality level (1-5)"),
            ParamSpec("arch", str, default="", help_text="Target architecture (x86, x86_64, arm, etc.)"),
            ParamSpec("search_string", str, default="", help_text="Specific gadget pattern to search for"),
            ParamSpec("additional_args", str, default="", help_text="Additional ropper arguments"),
        ],
        build_command=_ropper_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="libc-database",
        mcp_tool_name="libc_database_lookup",
        endpoint="/api/tools/libc-database",
        category="binary_analysis",
        description="Execute libc-database for libc identification and offset lookup.",
        params=[
            ParamSpec("action", str, default="find", help_text="Action to perform (find, dump, download)"),
            ParamSpec("symbols", str, default="", help_text="Symbols with offsets for find action (format: 'symbol1:offset1 symbol2:offset2')"),
            ParamSpec("libc_id", str, default="", help_text="Libc ID for dump/download actions"),
            ParamSpec("additional_args", str, default="", help_text="Additional arguments"),
        ],
        build_command=_libc_database_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="objdump",
        mcp_tool_name="objdump_analyze",
        endpoint="/api/tools/objdump",
        category="binary_analysis",
        description="Analyze a binary using objdump.",
        params=[
            ParamSpec("binary", str, required=True, help_text="Path to the binary file"),
            ParamSpec("disassemble", bool, default=True, help_text="Whether to disassemble the binary"),
            ParamSpec("additional_args", str, default="", help_text="Additional objdump arguments"),
        ],
        build_command=_objdump_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="strings",
        mcp_tool_name="strings_extract",
        endpoint="/api/tools/strings",
        category="binary_analysis",
        description="Extract strings from a binary file.",
        params=[
            ParamSpec("file_path", str, required=True, help_text="Path to the file"),
            ParamSpec("min_len", int, default=4, help_text="Minimum string length"),
            ParamSpec("additional_args", str, default="", help_text="Additional strings arguments"),
        ],
        build_command=_strings_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="xxd",
        mcp_tool_name="xxd_hexdump",
        endpoint="/api/tools/xxd",
        category="binary_analysis",
        description="Create a hex dump of a file using xxd.",
        params=[
            ParamSpec("file_path", str, required=True, help_text="Path to the file"),
            ParamSpec("offset", str, default="0", help_text="Offset to start reading from"),
            ParamSpec("length", str, default="", help_text="Number of bytes to read"),
            ParamSpec("additional_args", str, default="", help_text="Additional xxd arguments"),
        ],
        build_command=_xxd_command,
        use_recovery=True,
    ),
]

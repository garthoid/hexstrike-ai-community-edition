import time

from backend.server_core.file_ops import file_manager
from backend.server_core.python_env_manager import env_manager
from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _execute_python_script_build_command(p: dict) -> str:
    filename = p["filename"] or f"script_{int(time.time())}.py"
    p["filename"] = filename

    script_result = file_manager.create_file(filename, p["script"])
    if not script_result["success"]:
        raise RuntimeError(script_result.get("error", "Failed to create script file"))

    python_path = env_manager.get_python_path(p["env_name"])
    return f"{python_path} {script_result['path']}"


def _execute_python_script_postprocess(raw: dict, p: dict) -> dict:
    file_manager.delete_file(p["filename"])

    if isinstance(raw, dict):
        raw["env_name"] = p["env_name"]
        raw["script_filename"] = p["filename"]

    return raw


SPECS = [
    ToolSpec(
        name="execute_python_script",
        mcp_tool_name="execute_python_script",
        endpoint="/api/python/execute",
        category="python_env",
        description="Execute a Python script in a virtual environment on the API server.",
        params=[
            ParamSpec("script", str, required=True, help_text="Python script content to execute"),
            ParamSpec("env_name", str, default="default", help_text="Name of the virtual environment"),
            ParamSpec("filename", str, default="", help_text="Custom script filename (auto-generated if empty)"),
        ],
        build_command=_execute_python_script_build_command,
        postprocess=_execute_python_script_postprocess,
        use_cache=False,
    ),
]

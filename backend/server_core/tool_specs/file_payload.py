import random
import string
import time

from backend.server_core.file_ops import file_manager
from backend.server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _create_file_handler(p: dict) -> dict:
    return file_manager.create_file(p["filename"], p["content"], p["binary"])


def _modify_file_handler(p: dict) -> dict:
    return file_manager.modify_file(p["filename"], p["content"], p["append"])


def _delete_file_handler(p: dict) -> dict:
    return file_manager.delete_file(p["filename"])


def _list_files_handler(p: dict) -> dict:
    return file_manager.list_files(p["directory"])


def _generate_payload_handler(p: dict) -> dict:
    payload_type = p["payload_type"]
    size = p["size"]
    pattern = p["pattern"]
    filename = p["filename"] or f"payload_{int(time.time())}"

    if size > 100 * 1024 * 1024:  # 100MB limit
        raise ToolValidationError("Payload size too large (max 100MB)")

    if payload_type == "buffer":
        content = pattern * (size // len(pattern))
    elif payload_type == "cyclic":
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        content = ""
        for i in range(size):
            content += alphabet[i % len(alphabet)]
    elif payload_type == "random":
        content = "".join(random.choices(string.ascii_letters + string.digits, k=size))
    else:
        raise ToolValidationError("Invalid payload type")

    result = file_manager.create_file(filename, content)
    result["payload_info"] = {
        "type": payload_type,
        "size": size,
        "pattern": pattern,
    }
    return result


SPECS = [
    ToolSpec(
        name="create_file",
        mcp_tool_name="create_file",
        endpoint="/api/files/create",
        category="file_payload",
        description="Create a file with specified content on the API server.",
        params=[
            ParamSpec("filename", str, required=True, help_text="Name of the file to create"),
            ParamSpec("content", str, default="", help_text="Content to write to the file"),
            ParamSpec("binary", bool, default=False, help_text="Whether the content is binary data"),
        ],
        handler=_create_file_handler,
    ),
    ToolSpec(
        name="modify_file",
        mcp_tool_name="modify_file",
        endpoint="/api/files/modify",
        category="file_payload",
        description="Modify an existing file on the API server.",
        params=[
            ParamSpec("filename", str, required=True, help_text="Name of the file to modify"),
            ParamSpec("content", str, default="", help_text="Content to write or append"),
            ParamSpec(
                "append", bool, default=False,
                help_text="Whether to append to the file (True) or overwrite (False)",
            ),
        ],
        handler=_modify_file_handler,
    ),
    ToolSpec(
        name="delete_file",
        mcp_tool_name="delete_file",
        endpoint="/api/files/delete",
        category="file_payload",
        description="Delete a file or directory on the API server.",
        method="DELETE",
        params=[
            ParamSpec("filename", str, required=True, help_text="Name of the file or directory to delete"),
        ],
        handler=_delete_file_handler,
    ),
    ToolSpec(
        name="list_files",
        mcp_tool_name="list_files",
        endpoint="/api/files/list",
        category="file_payload",
        description="List files in a directory on the API server.",
        method="GET",
        params=[
            ParamSpec(
                "directory", str, default=".",
                help_text="Directory to list (relative to server's base directory)",
            ),
        ],
        handler=_list_files_handler,
    ),
    ToolSpec(
        name="generate_payload",
        mcp_tool_name="generate_payload",
        endpoint="/api/payloads/generate",
        category="file_payload",
        description="Generate large payloads for testing and exploitation.",
        params=[
            ParamSpec("payload_type", str, default="buffer", help_text="Type of payload (buffer, cyclic, random)"),
            ParamSpec("size", int, default=1024, help_text="Size of the payload in bytes"),
            ParamSpec("pattern", str, default="A", help_text="Pattern to use for buffer payloads"),
            ParamSpec("filename", str, default="", help_text="Custom filename (auto-generated if empty)"),
        ],
        handler=_generate_payload_handler,
    ),
]

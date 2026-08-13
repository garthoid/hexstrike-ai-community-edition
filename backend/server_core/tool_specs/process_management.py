import logging

import backend.server_api.ops.process_management as process_management_api
from backend.server_core.process_manager import AITaskManager, ProcessManager
from backend.server_core.tool_spec import ParamSpec, ToolNotFoundError, ToolSpec

logger = logging.getLogger(__name__)


def _list_active_processes_handler(p: dict) -> dict:
    processes = ProcessManager.list_active_processes()

    safe_processes = {}
    for pid, info in processes.items():
        process_management_api._annotate_process(info)
        safe_processes[str(pid)] = process_management_api._json_safe_process(info)

    ai_tasks = AITaskManager.list_active_tasks()
    for task_id, info in ai_tasks.items():
        safe_processes[f"ai:{task_id}"] = {
            "pid": None,
            "task_id": task_id,
            "command": info.get("label", "ai_task"),
            "status": info.get("status", "running"),
            "start_time": info.get("start_time", 0),
            "progress": 0.0,
            "last_output": "",
            "bytes_processed": 0,
            "session_id": info.get("session_id", ""),
            "ai_task": True,
        }

    return {
        "success": True,
        "active_processes": safe_processes,
        "total_count": len(safe_processes),
    }


def _get_process_status_handler(p: dict) -> dict:
    pid = p["pid"]
    process_info = ProcessManager.get_process_status(pid)

    if process_info:
        process_management_api._annotate_process(process_info)
        return {
            "success": True,
            "process": process_management_api._json_safe_process(process_info),
        }

    raise ToolNotFoundError(f"Process {pid} not found")


def _terminate_process_handler(p: dict) -> dict:
    pid = p["pid"]
    success = ProcessManager.terminate_process(pid)

    if success:
        logger.info(f"Process {pid} terminated successfully")
        return {"success": True, "message": f"Process {pid} terminated successfully"}

    raise ToolNotFoundError(f"Failed to terminate process {pid} or process not found")


def _pause_process_handler(p: dict) -> dict:
    pid = p["pid"]
    success = ProcessManager.pause_process(pid)

    if success:
        logger.info(f"Process {pid} paused successfully")
        return {"success": True, "message": f"Process {pid} paused successfully"}

    raise ToolNotFoundError(f"Failed to pause process {pid} or process not found")


def _resume_process_handler(p: dict) -> dict:
    pid = p["pid"]
    success = ProcessManager.resume_process(pid)

    if success:
        logger.info(f"Process {pid} resumed successfully")
        return {"success": True, "message": f"Process {pid} resumed successfully"}

    raise ToolNotFoundError(f"Failed to resume process {pid} or process not found")


def _get_process_dashboard_handler(p: dict) -> dict:
    return process_management_api._build_dashboard_payload()


SPECS = [
    ToolSpec(
        name="list_active_processes",
        mcp_tool_name="list_active_processes",
        endpoint="/api/processes/list",
        category="process_management",
        description="List all active processes on the API server.",
        method="GET",
        handler=_list_active_processes_handler,
    ),
    ToolSpec(
        name="get_process_status",
        mcp_tool_name="get_process_status",
        endpoint="/api/processes/status/<int:pid>",
        category="process_management",
        description="Get the status of a specific process.",
        params=[
            ParamSpec("pid", int, required=True, help_text="Process ID to check"),
        ],
        method="GET",
        handler=_get_process_status_handler,
    ),
    ToolSpec(
        name="terminate_process",
        mcp_tool_name="terminate_process",
        endpoint="/api/processes/terminate/<int:pid>",
        category="process_management",
        description="Terminate a specific running process.",
        params=[
            ParamSpec("pid", int, required=True, help_text="Process ID to terminate"),
        ],
        method="POST",
        handler=_terminate_process_handler,
    ),
    ToolSpec(
        name="pause_process",
        mcp_tool_name="pause_process",
        endpoint="/api/processes/pause/<int:pid>",
        category="process_management",
        description="Pause a specific running process.",
        params=[
            ParamSpec("pid", int, required=True, help_text="Process ID to pause"),
        ],
        method="POST",
        handler=_pause_process_handler,
    ),
    ToolSpec(
        name="resume_process",
        mcp_tool_name="resume_process",
        endpoint="/api/processes/resume/<int:pid>",
        category="process_management",
        description="Resume a paused process.",
        params=[
            ParamSpec("pid", int, required=True, help_text="Process ID to resume"),
        ],
        method="POST",
        handler=_resume_process_handler,
    ),
    ToolSpec(
        name="get_process_dashboard",
        mcp_tool_name="get_process_dashboard",
        endpoint="/api/processes/dashboard",
        category="process_management",
        description="Get enhanced process dashboard with visual status indicators.",
        method="GET",
        handler=_get_process_dashboard_handler,
    ),
]

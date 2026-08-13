from datetime import datetime

from backend.server_core.singletons import error_handler
from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _error_handling_statistics_handler(p: dict) -> dict:
    return {
        "success": True,
        "statistics": error_handler.get_error_statistics(),
        "timestamp": datetime.now().isoformat(),
    }


def _test_error_recovery_handler(p: dict) -> dict:
    error_type = p["error_type"]
    if error_type == "timeout":
        exception = TimeoutError("Simulated timeout error")
    elif error_type == "permission_denied":
        exception = PermissionError("Simulated permission error")
    elif error_type == "network_unreachable":
        exception = ConnectionError("Simulated network error")
    else:
        exception = Exception(f"Simulated {error_type} error")

    context = {"target": p["target"], "parameters": {}, "attempt_count": 1}
    recovery_strategy = error_handler.handle_tool_failure(p["tool_name"], exception, context)

    return {
        "success": True,
        "recovery_strategy": {
            "action": recovery_strategy.action.value,
            "parameters": recovery_strategy.parameters,
            "max_attempts": recovery_strategy.max_attempts,
            "success_probability": recovery_strategy.success_probability,
            "estimated_time": recovery_strategy.estimated_time,
        },
        "error_classification": error_handler.classify_error(str(exception), exception).value,
        "alternative_tools": error_handler.tool_alternatives.get(p["tool_name"], []),
        "timestamp": datetime.now().isoformat(),
    }


SPECS = [
    ToolSpec(
        name="error_handling_statistics",
        mcp_tool_name="error_handling_statistics",
        endpoint="/api/error-handling/statistics",
        category="error_handling",
        description="Get intelligent error handling system statistics and recent error patterns.",
        method="GET",
        handler=_error_handling_statistics_handler,
    ),
    ToolSpec(
        name="test_error_recovery",
        mcp_tool_name="test_error_recovery",
        endpoint="/api/error-handling/test-recovery",
        category="error_handling",
        description="Test the intelligent error recovery system with simulated failures.",
        params=[
            ParamSpec("tool_name", str, required=True, help_text="Name of tool to simulate error for"),
            ParamSpec(
                "error_type", str, default="timeout",
                help_text="Type of error to simulate (timeout, permission_denied, network_unreachable, etc.)",
            ),
            ParamSpec("target", str, default="example.invalid", help_text="Target for the simulated test"),
        ],
        handler=_test_error_recovery_handler,
    ),
]

from backend.server_core.singletons import db, llm_client
from backend.server_core.tool_spec import ParamSpec, ToolNotFoundError, ToolSpec


def _llm_agent_scan_result_handler(p: dict) -> dict:
    session_id = p["session_id"]

    if db is None:
        return {"success": False, "error": "Database not available"}

    session = db.get_llm_session(session_id)
    if not session:
        raise ToolNotFoundError(f"Session '{session_id}' not found")

    vulnerabilities = db.get_llm_vulnerabilities(session_id)

    return {
        "success": True,
        "session": session,
        "vulnerabilities": vulnerabilities,
    }


def _llm_status_handler(p: dict) -> dict:
    status = llm_client.status()
    return {"success": True, **status}


SPECS = [
    ToolSpec(
        name="llm_agent_scan_result",
        mcp_tool_name="llm_agent_scan_result",
        endpoint="/api/intelligence/llm-agent-scan/<session_id>",
        category="ai_assist",
        description="Retrieve the results of a completed LLM agent scan session.",
        params=[
            ParamSpec("session_id", str, required=True, help_text="The session ID returned by llm_agent_scan"),
        ],
        method="GET",
        handler=_llm_agent_scan_result_handler,
    ),
    ToolSpec(
        name="llm_status",
        mcp_tool_name="llm_status",
        endpoint="/api/intelligence/llm-status",
        category="ai_assist",
        description="Check whether the LLM backend is available and report its configuration.",
        method="GET",
        handler=_llm_status_handler,
    ),
]

import uuid as _uuid
from datetime import datetime

from backend.server_core.singletons import db, llm_client, run_history, session_store
from backend.server_core.tool_spec import ParamSpec, ToolNotFoundError, ToolSpec


def _save_session_note(session_id: str, result: dict, folder: str, base_prefix: str, formatter) -> str | None:
    target = result.get("target", session_id)
    objective = result.get("objective", "")
    md_content = formatter(result, session_id, target, objective)
    base = f"{base_prefix}{datetime.now().strftime('%Y-%m-%d')}"
    for i in range(20):
        name = base if i == 0 else f"{base}-{i + 1}"
        if not session_store.note_exists(session_id, name, folder):
            if session_store.save_note(session_id, name, md_content, folder):
                return f"notes/{folder}/{name}.md"
            break
    return None


def _run_ai_task(task_id: str, label: str, session_id: str, fn):
    from backend.server_core.process_manager import AITaskManager

    AITaskManager.register_task(task_id, label, session_id=session_id)
    try:
        result = fn()
        cancelled = AITaskManager.is_cancelled(task_id)
    finally:
        AITaskManager.unregister_task(task_id)
    return result, cancelled


def _analyze_session_handler(p: dict) -> dict:
    from backend.server_core.llm_agent import analyze_session, format_analysis_md

    session_id = p["session_id"]
    save_to_notes = bool(p.get("save_to_notes"))

    task_id = f"ai_analyze_{_uuid.uuid4().hex[:8]}"
    result, cancelled = _run_ai_task(
        task_id,
        "ai_analyze_session",
        session_id,
        lambda: analyze_session(session_id=session_id, llm_client=llm_client, db=db, run_history=run_history),
    )

    if cancelled:
        return {"success": False, "error": "Analysis was cancelled"}

    response = dict(result)
    if result.get("success") and save_to_notes:
        saved_path = _save_session_note(session_id, result, "analysis", "analysis-", format_analysis_md)
        if saved_path:
            response["saved_path"] = saved_path

    return response


def _follow_up_session_handler(p: dict) -> dict:
    from backend.server_core.llm_agent import follow_up_session, format_followup_md

    session_id = p["session_id"]
    save_to_notes = bool(p.get("save_to_notes"))

    task_id = f"ai_followup_{_uuid.uuid4().hex[:8]}"
    result, cancelled = _run_ai_task(
        task_id,
        "ai_follow_up_session",
        session_id,
        lambda: follow_up_session(session_id=session_id, llm_client=llm_client, db=db, run_history=run_history),
    )

    if cancelled:
        return {"success": False, "error": "Follow-up was cancelled"}

    response = dict(result)
    if result.get("success") and save_to_notes:
        saved_path = _save_session_note(session_id, result, "follow-up", "follow-up-", format_followup_md)
        if saved_path:
            response["saved_path"] = saved_path

    return response


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
        name="analyze_session",
        mcp_tool_name="analyze_session",
        endpoint="/api/intelligence/analyze-session",
        category="ai_assist",
        description=(
            "Analyse an existing NyxStrike workflow session using the LLM. Fetches all "
            "tool run logs associated with the session, sends them to the configured LLM "
            "for interpretation, and persists structured vulnerability findings to "
            "NyxStrikeDB. The LLM does NOT dispatch any tools — this is a pure analysis "
            "pass over already-executed output."
        ),
        params=[
            ParamSpec("session_id", str, required=True, help_text="A sess_ prefixed session ID from SessionStore"),
            ParamSpec("save_to_notes", bool, default=False, help_text="Save the analysis as a note under notes/analysis/"),
        ],
        method="POST",
        handler=_analyze_session_handler,
    ),
    ToolSpec(
        name="follow_up_session",
        mcp_tool_name="follow_up_session",
        endpoint="/api/intelligence/follow-up-session",
        category="ai_assist",
        description=(
            "Produce a prioritised follow-up action plan for an existing NyxStrike session. "
            "Reads all tool run logs and existing findings for the session, then asks the "
            "configured LLM to plan the next concrete tool invocations with parameters."
        ),
        params=[
            ParamSpec("session_id", str, required=True, help_text="A sess_ prefixed session ID from SessionStore"),
            ParamSpec("save_to_notes", bool, default=True, help_text="Save the plan as a note under notes/follow-up/"),
        ],
        method="POST",
        handler=_follow_up_session_handler,
    ),
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

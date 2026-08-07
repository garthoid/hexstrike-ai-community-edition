"""
server_api/ai_assist/llm_agent_api.py


Endpoints:
  GET  /api/intelligence/llm-agent-sessions
      List recent LLM agent sessions (default: last 50).

"""

import logging

from flask import Blueprint, jsonify, request

from backend.server_core.singletons import db

logger = logging.getLogger(__name__)

api_ai_assist_llm_agent_bp = Blueprint("api_ai_assist_llm_agent", __name__)


@api_ai_assist_llm_agent_bp.route("/api/intelligence/llm-agent-sessions", methods=["GET"])
def llm_agent_sessions():
  """List recent LLM agent scan sessions."""
  try:
    if db is None:
      return jsonify({"success": False, "error": "Database not available"}), 503

    limit = min(int(request.args.get("limit", 50)), 200)
    sessions = db.list_llm_sessions(limit=limit)
    return jsonify({"success": True, "sessions": sessions, "count": len(sessions)})

  except Exception as exc:
    logger.exception("llm_agent_api: error listing sessions")
    return jsonify({"success": False, "error": str(exc)}), 500



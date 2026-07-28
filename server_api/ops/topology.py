"""
Topology API — exports a completed recon tool run into a session's network
topology graph (hosts/ports), auto-creating the session if none was given.

Routes:
  POST /api/topology/export   parse a tool result and merge it into a session
"""

import logging

from flask import Blueprint, jsonify, request

from server_core.session_flow import append_event, create_session, load_session_any, now_ts, update_session
from server_core.topology_extractor import TOPOLOGY_PARSERS, extract_topology, merge_topology

logger = logging.getLogger(__name__)

api_topology_bp = Blueprint("topology", __name__)

_TARGET_PARAM_KEYS = ["target", "url", "domain", "host", "ip", "rhost", "hostname"]


def _derive_target(params: dict) -> str:
  for key in _TARGET_PARAM_KEYS:
    value = params.get(key)
    if value is None:
      continue
    trimmed = str(value).strip()
    if trimmed:
      return trimmed
  return "unknown"


@api_topology_bp.route("/api/topology/export", methods=["POST"])
def export_topology():
  """Parse a completed tool run's stdout and merge it into a session's topology."""
  try:
    data = request.get_json(force=True) or {}
    tool = str(data.get("tool", "")).strip()
    params = data.get("params", {}) if isinstance(data.get("params"), dict) else {}
    result = data.get("result", {}) if isinstance(data.get("result"), dict) else {}
    session_id = data.get("session_id")

    if tool not in TOPOLOGY_PARSERS:
      return jsonify({"success": False, "error": f"Tool '{tool}' does not support topology export"}), 400

    parsed = extract_topology(tool, result.get("stdout", ""))
    if not parsed:
      return jsonify({"success": True, "topology": None, "message": "No hosts/ports found in output"})

    if session_id:
      loaded = load_session_any(session_id)
      if not loaded:
        return jsonify({"success": False, "error": "Session not found"}), 404
      session_data, _state = loaded
    else:
      target = str(data.get("target", "")).strip() or _derive_target(params)
      session_data = create_session(
        target=target,
        steps=[{"tool": tool, "parameters": params}],
        source="topology_export",
        objective="Network topology mapping",
        name=f"Topology — {target}",
      )
      session_id = session_data["session_id"]

    merged = merge_topology(session_data.get("topology"), parsed, tool, now_ts())
    update_session(session_id, {"topology": merged})
    append_event(
      session_id,
      "topology_updated",
      f"Topology updated from {tool} run ({len(parsed['hosts'])} host(s), {len(parsed['ports'])} port(s))",
      {"tool": tool},
    )

    return jsonify({
      "success": True,
      "session_id": session_id,
      "topology": {"hosts": merged["hosts"], "ports": merged["ports"]},
    })
  except Exception as e:
    logger.error(f"Error exporting topology: {e}")
    return jsonify({"success": False, "error": str(e)}), 500

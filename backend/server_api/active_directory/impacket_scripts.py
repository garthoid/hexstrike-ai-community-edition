from flask import Blueprint, request, jsonify

from backend.server_core.impacket_helpers import get_impacket_script_spec

api_tools_impacket_bp = Blueprint("api_tools_impacket", __name__)


@api_tools_impacket_bp.route("/api/tool/active_directory/impacket/spec", methods=["POST"])
def get_impacket_spec():
    """
    Helper endpoint so UI/agent can discover required args for a script.
    """
    try:
        payload = request.get_json(silent=True) or {}
        script_name = payload.get("script", "").strip()

        spec = get_impacket_script_spec(script_name)
        return jsonify({
            "script": spec["script"],
            "binary": spec["binary"],
            "usage": spec["usage"],
            "required_positionals": spec["required_positionals"],
            "options": spec["options"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

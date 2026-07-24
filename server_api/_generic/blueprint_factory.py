"""Generic Flask blueprint factory driven by a ToolSpec.

Replaces the ~25-line hand-written boilerplate every server_api tool file used to
repeat (param extraction/validation, command build, execute_command call, jsonify,
try/except -> 500) with a single data-driven implementation.
"""

import logging

from flask import Blueprint, jsonify, request

from server_core.command_executor import execute_command
from server_core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


def make_blueprint(spec: ToolSpec) -> Blueprint:
    bp = Blueprint(f"api_{spec.category}_{spec.name}", __name__)

    @bp.route(spec.endpoint, methods=["POST"], endpoint=spec.name)
    def _view():
        try:
            data = request.get_json(force=True, silent=True) or {}
            params = {}
            for p in spec.params:
                value = data.get(p.name, p.default if not p.required else "")
                if p.required and not value:
                    return jsonify({"error": f"{p.name} parameter is required"}), 400
                params[p.name] = value

            commands = spec.build_command(params)
            if isinstance(commands, str):
                raw = execute_command(
                    commands,
                    use_cache=spec.use_cache,
                    timeout=spec.timeout,
                    use_recovery=spec.use_recovery,
                )
            else:
                raw = [
                    execute_command(
                        cmd,
                        use_cache=spec.use_cache,
                        timeout=spec.timeout,
                        use_recovery=spec.use_recovery,
                    )
                    for cmd in commands
                ]

            result = spec.postprocess(raw, params) if spec.postprocess else raw
            return jsonify(result)
        except Exception as e:
            logger.error(f"💥 Error in {spec.name} endpoint: {e}")
            return jsonify({"error": f"Server error: {e}"}), 500

    return bp

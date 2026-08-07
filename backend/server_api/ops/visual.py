from flask import Blueprint, jsonify, request
from datetime import datetime
from backend.server_core.intelligence.cve_intelligence_manager import CVEIntelligenceManager

import logging
logger = logging.getLogger(__name__)


api_visual_bp = Blueprint("visual", __name__)

@api_visual_bp.route("/api/visual/vulnerability-card", methods=["POST"])
def create_vulnerability_card():
    """Create a beautiful vulnerability card using CVEIntelligenceManager"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Create vulnerability card
        cve_intelligence = CVEIntelligenceManager()
        card = cve_intelligence.render_vulnerability_card(data)

        return jsonify({
            "success": True,
            "vulnerability_card": card,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"💥 Error creating vulnerability card: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


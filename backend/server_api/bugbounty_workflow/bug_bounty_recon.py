from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from backend.server_core.workflows.bugbounty.target import BugBountyTarget
from backend.server_core.singletons import bugbounty_manager
from backend.server_core.session_flow import create_session, extract_workflow_steps

logger = logging.getLogger(__name__)

api_bugbounty_workflow_bug_bounty_recon_bp = Blueprint("api_bugbounty_workflow_bug_bounty_recon", __name__)


@api_bugbounty_workflow_bug_bounty_recon_bp.route("/api/bugbounty/comprehensive-assessment", methods=["POST"])
def create_comprehensive_bugbounty_assessment():
    """Create comprehensive bug bounty assessment combining all workflows"""
    try:
        data = request.get_json()
        if not data or 'domain' not in data:
            return jsonify({"error": "Domain is required"}), 400

        domain = data['domain']
        scope = data.get('scope', [])
        priority_vulns = data.get('priority_vulns', ["rce", "sqli", "xss", "idor", "ssrf"])
        include_osint = data.get('include_osint', True)
        include_business_logic = data.get('include_business_logic', True)

        logger.info(f"Creating comprehensive bug bounty assessment for {domain}")

        target = BugBountyTarget(
            domain=domain,
            scope=scope,
            priority_vulns=priority_vulns
        )

        assessment = {
            "target": domain,
            "reconnaissance": bugbounty_manager.create_reconnaissance_workflow(target),
            "vulnerability_hunting": bugbounty_manager.create_vulnerability_hunting_workflow(target)
        }

        if include_osint:
            assessment["osint"] = bugbounty_manager.create_osint_workflow(target)

        if include_business_logic:
            assessment["business_logic"] = bugbounty_manager.create_business_logic_testing_workflow(target)

        total_time = sum(workflow.get("estimated_time", 0) for workflow in assessment.values() if isinstance(workflow, dict))
        total_tools = sum(workflow.get("tools_count", 0) for workflow in assessment.values() if isinstance(workflow, dict))

        assessment["summary"] = {
            "total_estimated_time": total_time,
            "total_tools": total_tools,
            "workflow_count": len([k for k in assessment.keys() if k != "target"]),
            "priority_score": assessment["vulnerability_hunting"].get("priority_score", 0)
        }

        persisted = create_session(
            target=domain,
            steps=extract_workflow_steps(assessment, domain),
            source="mcp_bugbounty",
            objective="comprehensive_assessment",
            metadata={"origin": "api/bugbounty/comprehensive-assessment"},
        )

        logger.info(f"Comprehensive bug bounty assessment created for {domain}")

        return jsonify({
            "success": True,
            "assessment": assessment,
            "session_id": persisted.get("session_id"),
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error creating comprehensive assessment: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

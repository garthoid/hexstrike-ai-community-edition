import json
import logging
import time
from datetime import datetime

from backend.server_core.singletons import decision_engine
from backend.server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError
from backend.server_core.target_types import TechnologyStack

logger = logging.getLogger(__name__)


# ============================================================================
# SHARED RESPONSE WRAPPERS
# ============================================================================

def _wrap_success(payload: dict, stdout_payload: dict, start_time: float) -> dict:
    return {
        "success": True,
        **payload,
        "stdout": json.dumps(stdout_payload, indent=2),
        "stderr": "",
        "return_code": 0,
        "timed_out": False,
        "partial_results": False,
        "execution_time": time.time() - start_time,
        "timestamp": datetime.now().isoformat(),
    }


def _wrap_failure(exc: Exception, start_time: float) -> dict:
    return {
        "success": False,
        "error": f"Server error: {exc}",
        "stdout": "",
        "stderr": str(exc),
        "return_code": 1,
        "timed_out": False,
        "partial_results": False,
        "execution_time": time.time() - start_time,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# TARGET ANALYSIS HANDLERS
# ============================================================================

def _analyze_target_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]

    try:
        profile = decision_engine.analyze_target(target)
        profile_dict = profile.to_dict()
        stdout_payload = {
            "target": target,
            "target_type": profile.target_type.value,
            "risk_level": profile.risk_level,
            "target_profile": profile_dict,
        }
        return _wrap_success({"target_profile": profile_dict}, stdout_payload, start_time)
    except Exception as e:
        logger.error(f"Error analyzing target: {e}")
        return _wrap_failure(e, start_time)


def _select_optimal_tools_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]
    objective = p["objective"]
    planner_mode = p.get("planner_mode") or None

    try:
        profile = decision_engine.analyze_target(target)
        selected_tools = decision_engine.select_optimal_tools(profile, objective, planner_mode=planner_mode)
        profile_dict = profile.to_dict()
        payload = {
            "target": target,
            "objective": objective,
            "planner_mode": planner_mode if planner_mode else decision_engine.get_planner_mode(),
            "target_profile": profile_dict,
            "selected_tools": selected_tools,
            "tool_count": len(selected_tools),
        }
        stdout_payload = {
            "target": target,
            "objective": objective,
            "tool_count": len(selected_tools),
            "selected_tools": selected_tools,
            "target_profile": profile_dict,
        }
        return _wrap_success(payload, stdout_payload, start_time)
    except Exception as e:
        logger.error(f"Error selecting tools: {e}")
        return _wrap_failure(e, start_time)


def _optimize_tool_parameters_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]
    tool = p["tool"]
    context = p.get("context") or {}

    try:
        logger.info(f"Optimizing parameters for {tool} against {target}")

        profile = decision_engine.analyze_target(target)
        optimized_params = decision_engine.optimize_parameters(tool, profile, context)

        logger.info(f"Parameters optimized for {tool}")

        profile_dict = profile.to_dict()
        payload = {
            "target": target,
            "tool": tool,
            "context": context,
            "target_profile": profile_dict,
            "optimized_parameters": optimized_params,
        }
        stdout_payload = {
            "target": target,
            "tool": tool,
            "optimized_parameters": optimized_params,
            "target_profile": profile_dict,
        }
        return _wrap_success(payload, stdout_payload, start_time)
    except Exception as e:
        logger.error(f"Error optimizing parameters for {tool}: {e}")
        return _wrap_failure(e, start_time)


def _detect_technologies_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]

    try:
        profile = decision_engine.analyze_target(target)

        tech_recommendations = {}
        for tech in profile.technologies:
            if tech == TechnologyStack.WORDPRESS:
                tech_recommendations["WordPress"] = {
                    "tools": ["wpscan", "nuclei"],
                    "focus_areas": ["plugin vulnerabilities", "theme issues", "user enumeration"],
                    "priority": "high",
                }
            elif tech == TechnologyStack.PHP:
                tech_recommendations["PHP"] = {
                    "tools": ["nikto", "sqlmap", "ffuf"],
                    "focus_areas": ["code injection", "file inclusion", "SQL injection"],
                    "priority": "high",
                }
            elif tech == TechnologyStack.NODEJS:
                tech_recommendations["Node.js"] = {
                    "tools": ["nuclei", "ffuf"],
                    "focus_areas": ["prototype pollution", "dependency vulnerabilities"],
                    "priority": "medium",
                }

        profile_dict = profile.to_dict()
        payload = {
            "target": target,
            "detected_technologies": [tech.value for tech in profile.technologies],
            "cms_type": profile.cms_type,
            "technology_recommendations": tech_recommendations,
            "target_profile": profile_dict,
        }
        return _wrap_success(payload, dict(payload), start_time)
    except Exception as e:
        logger.error(f"Error in technology detection: {e}")
        return _wrap_failure(e, start_time)


# ============================================================================
# ATTACK CHAIN HANDLERS
# ============================================================================

def _create_attack_chain_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]
    objective = p["objective"]

    from backend.server_api.ops.vulnerability_intelligence import _build_attack_chain_response

    try:
        payload = _build_attack_chain_response(
            target=target, objective=objective, persist=True, origin="api/intelligence/create-attack-chain"
        )
        return _wrap_success(payload, dict(payload), start_time)
    except Exception as e:
        logger.error(f"Error creating attack chain: {e}")
        return _wrap_failure(e, start_time)


def _preview_attack_chain_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]
    objective = p["objective"]

    from backend.server_api.ops.vulnerability_intelligence import _build_attack_chain_response

    try:
        payload = _build_attack_chain_response(
            target=target, objective=objective, persist=False, origin="api/intelligence/preview-attack-chain"
        )
        return _wrap_success(payload, dict(payload), start_time)
    except Exception as e:
        logger.error(f"Error previewing attack chain: {e}")
        return _wrap_failure(e, start_time)


# ============================================================================
# SMART SCAN HANDLER
# ============================================================================

def _smart_scan_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]
    objective = p["objective"]
    planner_mode = p.get("planner_mode") or None
    session_id = p.get("session_id") or None

    try:
        max_tools = int(p.get("max_tools", 5))
    except (TypeError, ValueError):
        raise ToolValidationError("max_tools must be an integer", success=False)

    if max_tools < 1:
        raise ToolValidationError("max_tools must be >= 1", success=False)

    max_tools = min(max_tools, 50)

    logger.info(f"Starting intelligent smart scan for {target}")

    from backend.server_api.ops.vulnerability_intelligence import _run_smart_scan

    try:
        scan_results = _run_smart_scan(target, objective, planner_mode, session_id, max_tools)
    except Exception as e:
        logger.error(f"Error in intelligent smart scan: {e}")
        return _wrap_failure(e, start_time)

    logger.info(f"Intelligent smart scan completed for {target}")
    stdout_text = scan_results.get("combined_output", "") or json.dumps(scan_results, indent=2)

    return {
        "success": True,
        "scan_results": scan_results,
        "stdout": stdout_text,
        "stderr": "",
        "return_code": 0,
        "timed_out": False,
        "partial_results": False,
        "execution_time": time.time() - start_time,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================================
# AI WORKFLOW HANDLERS
# ============================================================================

def _ai_reconnaissance_workflow_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]
    depth = p["depth"]

    try:
        profile = decision_engine.analyze_target(target)
    except Exception as e:
        logger.error(f"Error analyzing target: {e}")
        return _wrap_failure(e, start_time)

    objective = "comprehensive" if depth == "deep" else "quick" if depth == "surface" else "comprehensive"

    from backend.server_api.ops.vulnerability_intelligence import _build_attack_chain_response, _run_smart_scan

    try:
        chain_payload = _build_attack_chain_response(
            target=target, objective=objective, persist=True, origin="mcp_ai_reconnaissance_workflow"
        )
    except Exception as e:
        logger.error(f"Error creating attack chain: {e}")
        return _wrap_failure(e, start_time)

    max_tools = 8 if depth == "deep" else 3 if depth == "surface" else 5

    try:
        scan_results = _run_smart_scan(target, objective, None, None, max_tools)
    except Exception as e:
        logger.error(f"Error in intelligent smart scan: {e}")
        return _wrap_failure(e, start_time)

    logger.info(f"AI reconnaissance workflow completed for {target}")

    profile_dict = profile.to_dict()
    payload = {
        "target": target,
        "depth": depth,
        "target_analysis": profile_dict,
        "attack_chain": chain_payload.get("attack_chain", {}),
        "scan_results": scan_results,
    }
    stdout_payload = {
        "target": target,
        "depth": depth,
        "total_vulnerabilities": scan_results.get("total_vulnerabilities", 0),
        "target_analysis": profile_dict,
        "scan_results": scan_results,
    }
    return _wrap_success(payload, stdout_payload, start_time)


def _ai_vulnerability_assessment_handler(p: dict) -> dict:
    start_time = time.time()
    target = p["target"]
    focus_areas = p["focus_areas"]

    try:
        profile = decision_engine.analyze_target(target)
    except Exception as e:
        logger.error(f"Error analyzing target: {e}")
        return _wrap_failure(e, start_time)

    profile_dict = profile.to_dict()
    target_type = profile_dict.get("target_type", "unknown")

    if focus_areas == "all":
        objective = "comprehensive"
    elif "web" in focus_areas and target_type == "web_application":
        objective = "comprehensive"
    elif "network" in focus_areas and target_type == "network_host":
        objective = "comprehensive"
    else:
        objective = "quick"

    from backend.server_api.ops.vulnerability_intelligence import _run_smart_scan

    try:
        scan_results = _run_smart_scan(target, objective, None, None, 6)
    except Exception as e:
        logger.error(f"Error in intelligent smart scan: {e}")
        return _wrap_failure(e, start_time)

    logger.info(f"AI vulnerability assessment completed for {target}")

    payload = {
        "target": target,
        "focus_areas": focus_areas,
        "target_analysis": profile_dict,
        "vulnerability_scan": scan_results,
        "risk_assessment": {
            "risk_level": profile_dict.get("risk_level", "unknown"),
            "attack_surface_score": profile_dict.get("attack_surface_score", 0),
            "confidence_score": profile_dict.get("confidence_score", 0),
        },
    }
    stdout_payload = {
        "target": target,
        "focus_areas": focus_areas,
        "total_vulnerabilities": scan_results.get("total_vulnerabilities", 0),
        "risk_assessment": payload["risk_assessment"],
        "vulnerability_scan": scan_results,
    }
    return _wrap_success(payload, stdout_payload, start_time)


# ============================================================================
# TOOL SPECS
# ============================================================================

SPECS = [
    ToolSpec(
        name="analyze_target",
        mcp_tool_name="analyze_target_intelligence",
        endpoint="/api/intelligence/analyze-target",
        category="decision_engine",
        description="Analyze target using AI-powered intelligence to create comprehensive profile.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target URL, IP address, or domain to analyze"),
        ],
        handler=_analyze_target_handler,
    ),
    ToolSpec(
        name="select_optimal_tools",
        mcp_tool_name="select_optimal_tools_ai",
        endpoint="/api/intelligence/select-tools",
        category="decision_engine",
        description="Use AI to select optimal security tools based on target analysis and testing objective.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target to analyze"),
            ParamSpec("objective", str, default="comprehensive", help_text='Testing objective: "comprehensive", "quick", or "stealth"'),
            ParamSpec("planner_mode", str, default="", help_text='Override planner: "advanced" or "legacy" (leave blank for default)'),
        ],
        handler=_select_optimal_tools_handler,
    ),
    ToolSpec(
        name="optimize_tool_parameters",
        mcp_tool_name="optimize_tool_parameters_ai",
        endpoint="/api/intelligence/optimize-parameters",
        category="decision_engine",
        description="Use AI to optimize tool parameters based on target profile and context.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target to test"),
            ParamSpec("tool", str, required=True, help_text="Security tool to optimize"),
            ParamSpec("context", dict, default={}, help_text="Additional context object (e.g. stealth, aggressive)"),
        ],
        handler=_optimize_tool_parameters_handler,
    ),
    ToolSpec(
        name="preview_attack_chain",
        mcp_tool_name="preview_attack_chain_ai",
        endpoint="/api/intelligence/preview-attack-chain",
        category="decision_engine",
        description="Preview an intelligent attack chain without persisting a session.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target for the attack chain"),
            ParamSpec("objective", str, default="comprehensive", help_text='Attack objective: "comprehensive", "quick", or "stealth"'),
        ],
        handler=_preview_attack_chain_handler,
    ),
    ToolSpec(
        name="create_attack_chain",
        mcp_tool_name="create_attack_chain_ai",
        endpoint="/api/intelligence/create-attack-chain",
        category="decision_engine",
        description="Create an intelligent attack chain using AI-driven tool sequencing and optimization, persisted as a session.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target for the attack chain"),
            ParamSpec("objective", str, default="comprehensive", help_text='Attack objective: "comprehensive", "quick", or "stealth"'),
        ],
        handler=_create_attack_chain_handler,
    ),
    ToolSpec(
        name="smart_scan",
        mcp_tool_name="intelligent_smart_scan",
        endpoint="/api/intelligence/smart-scan",
        category="decision_engine",
        description="Execute an intelligent scan using AI-driven tool selection and parameter optimization, with parallel execution.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target to scan"),
            ParamSpec("objective", str, default="comprehensive", help_text='Scanning objective: "comprehensive", "quick", or "stealth"'),
            ParamSpec("max_tools", int, default=5, help_text="Maximum number of tools to use"),
            ParamSpec("planner_mode", str, default="", help_text='Override planner: "advanced" or "legacy" (leave blank for default)'),
            ParamSpec("session_id", str, default="", help_text="Existing session ID to associate this scan with"),
        ],
        handler=_smart_scan_handler,
    ),
    ToolSpec(
        name="detect_technologies",
        mcp_tool_name="detect_technologies_ai",
        endpoint="/api/intelligence/technology-detection",
        category="decision_engine",
        description="Use AI to detect technologies and provide technology-specific testing recommendations.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target to analyze for technology detection"),
        ],
        handler=_detect_technologies_handler,
    ),
    ToolSpec(
        name="ai_reconnaissance_workflow",
        mcp_tool_name="ai_reconnaissance_workflow",
        endpoint="/api/intelligence/reconnaissance-workflow",
        category="decision_engine",
        description="Execute AI-driven reconnaissance workflow with intelligent tool chaining (analyze target, create attack chain, run scan).",
        params=[
            ParamSpec("target", str, required=True, help_text="Target for reconnaissance"),
            ParamSpec("depth", str, default="standard", help_text='Reconnaissance depth: "surface", "standard", or "deep"'),
        ],
        handler=_ai_reconnaissance_workflow_handler,
    ),
    ToolSpec(
        name="ai_vulnerability_assessment",
        mcp_tool_name="ai_vulnerability_assessment",
        endpoint="/api/intelligence/vulnerability-assessment",
        category="decision_engine",
        description="Perform AI-driven vulnerability assessment with intelligent prioritization.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target for vulnerability assessment"),
            ParamSpec("focus_areas", str, default="all", help_text='Comma-separated focus areas: "web", "network", "api", "all"'),
        ],
        handler=_ai_vulnerability_assessment_handler,
    ),
]

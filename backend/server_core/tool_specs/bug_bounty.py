from datetime import datetime

from backend.server_core.singletons import bugbounty_manager, fileupload_framework
from backend.server_core.session_flow import create_session, extract_workflow_steps
from backend.server_core.tool_spec import ParamSpec, ToolSpec
from backend.server_core.workflows.bugbounty.target import BugBountyTarget


def _reconnaissance_workflow_handler(p: dict) -> dict:
    domain = p["domain"]
    scope = p["scope"].split(",") if p["scope"] else []
    out_of_scope = p["out_of_scope"].split(",") if p["out_of_scope"] else []
    program_type = p["program_type"]

    target = BugBountyTarget(
        domain=domain,
        scope=scope,
        out_of_scope=out_of_scope,
        program_type=program_type,
    )

    workflow = bugbounty_manager.create_reconnaissance_workflow(target)
    persisted = create_session(
        target=domain,
        steps=extract_workflow_steps(workflow, domain),
        source="mcp_bugbounty",
        objective="reconnaissance",
        metadata={"origin": "api/bugbounty/reconnaissance-workflow"},
    )

    return {
        "success": True,
        "workflow": workflow,
        "session_id": persisted.get("session_id"),
        "timestamp": datetime.now().isoformat(),
    }


def _vulnerability_hunting_handler(p: dict) -> dict:
    domain = p["domain"]
    priority_vulns = p["priority_vulns"].split(",") if p["priority_vulns"] else []
    bounty_range = p["bounty_range"]

    target = BugBountyTarget(
        domain=domain,
        priority_vulns=priority_vulns,
        bounty_range=bounty_range,
    )

    workflow = bugbounty_manager.create_vulnerability_hunting_workflow(target)
    persisted = create_session(
        target=domain,
        steps=extract_workflow_steps(workflow, domain),
        source="mcp_bugbounty",
        objective="vulnerability_hunting",
        metadata={"origin": "api/bugbounty/vulnerability-hunting-workflow"},
    )

    return {
        "success": True,
        "workflow": workflow,
        "session_id": persisted.get("session_id"),
        "timestamp": datetime.now().isoformat(),
    }


def _business_logic_workflow_handler(p: dict) -> dict:
    domain = p["domain"]
    program_type = p["program_type"]

    target = BugBountyTarget(domain=domain, program_type=program_type)

    workflow = bugbounty_manager.create_business_logic_testing_workflow(target)
    persisted = create_session(
        target=domain,
        steps=extract_workflow_steps(workflow, domain),
        source="mcp_bugbounty",
        objective="business_logic",
        metadata={"origin": "api/bugbounty/business-logic-workflow"},
    )

    return {
        "success": True,
        "workflow": workflow,
        "session_id": persisted.get("session_id"),
        "timestamp": datetime.now().isoformat(),
    }


def _osint_workflow_handler(p: dict) -> dict:
    domain = p["domain"]

    target = BugBountyTarget(domain=domain)

    workflow = bugbounty_manager.create_osint_workflow(target)
    persisted = create_session(
        target=domain,
        steps=extract_workflow_steps(workflow, domain),
        source="mcp_bugbounty",
        objective="osint",
        metadata={"origin": "api/bugbounty/osint-workflow"},
    )

    return {
        "success": True,
        "workflow": workflow,
        "session_id": persisted.get("session_id"),
        "timestamp": datetime.now().isoformat(),
    }


def _file_upload_testing_handler(p: dict) -> dict:
    target_url = p["target_url"]

    workflow = fileupload_framework.create_upload_testing_workflow(target_url)
    test_files = fileupload_framework.generate_test_files()
    workflow["test_files"] = test_files

    persisted = create_session(
        target=target_url,
        steps=extract_workflow_steps(workflow, target_url),
        source="mcp_bugbounty",
        objective="file_upload_testing",
        metadata={"origin": "api/bugbounty/file-upload-testing"},
    )

    return {
        "success": True,
        "workflow": workflow,
        "session_id": persisted.get("session_id"),
        "timestamp": datetime.now().isoformat(),
    }


def _comprehensive_assessment_handler(p: dict) -> dict:
    domain = p["domain"]
    scope = p["scope"].split(",") if p["scope"] else []
    priority_vulns = p["priority_vulns"].split(",") if p["priority_vulns"] else []
    include_osint = p["include_osint"]
    include_business_logic = p["include_business_logic"]

    target = BugBountyTarget(domain=domain, scope=scope, priority_vulns=priority_vulns)

    assessment = {
        "target": domain,
        "reconnaissance": bugbounty_manager.create_reconnaissance_workflow(target),
        "vulnerability_hunting": bugbounty_manager.create_vulnerability_hunting_workflow(target),
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
        "priority_score": assessment["vulnerability_hunting"].get("priority_score", 0),
    }

    persisted = create_session(
        target=domain,
        steps=extract_workflow_steps(assessment, domain),
        source="mcp_bugbounty",
        objective="comprehensive_assessment",
        metadata={"origin": "api/bugbounty/comprehensive-assessment"},
    )

    return {
        "success": True,
        "assessment": assessment,
        "session_id": persisted.get("session_id"),
        "timestamp": datetime.now().isoformat(),
    }


_AUTH_BYPASS_TECHNIQUES = {
    "form": [
        {"technique": "SQL Injection", "payloads": ["admin'--", "' OR '1'='1'--"]},
        {"technique": "Default Credentials", "payloads": ["admin:admin", "admin:password"]},
        {"technique": "Password Reset", "description": "Test password reset token reuse and manipulation"},
        {"technique": "Session Fixation", "description": "Test session ID prediction and fixation"},
    ],
    "jwt": [
        {"technique": "Algorithm Confusion", "description": "Change RS256 to HS256"},
        {"technique": "None Algorithm", "description": "Set algorithm to 'none'"},
        {"technique": "Key Confusion", "description": "Use public key as HMAC secret"},
        {"technique": "Token Manipulation", "description": "Modify claims and resign token"},
    ],
    "oauth": [
        {"technique": "Redirect URI Manipulation", "description": "Test open redirect in redirect_uri"},
        {"technique": "State Parameter", "description": "Test CSRF via missing/weak state parameter"},
        {"technique": "Code Reuse", "description": "Test authorization code reuse"},
        {"technique": "Client Secret", "description": "Test for exposed client secrets"},
    ],
    "saml": [
        {"technique": "XML Signature Wrapping", "description": "Manipulate SAML assertions"},
        {"technique": "XML External Entity", "description": "Test XXE in SAML requests"},
        {"technique": "Replay Attacks", "description": "Test assertion replay"},
        {"technique": "Signature Bypass", "description": "Test signature validation bypass"},
    ],
}


def _auth_bypass_testing_handler(p: dict) -> dict:
    target_url = p["target_url"]
    auth_type = p["auth_type"]

    workflow = {
        "target": target_url,
        "auth_type": auth_type,
        "bypass_techniques": _AUTH_BYPASS_TECHNIQUES.get(auth_type, []),
        "testing_phases": [
            {"phase": "reconnaissance", "description": "Identify authentication mechanisms"},
            {"phase": "baseline_testing", "description": "Test normal authentication flow"},
            {"phase": "bypass_testing", "description": "Apply bypass techniques"},
            {"phase": "privilege_escalation", "description": "Test for privilege escalation"},
        ],
        "estimated_time": 240,
        "manual_testing_required": True,
    }

    return {
        "success": True,
        "workflow": workflow,
        "timestamp": datetime.now().isoformat(),
    }


SPECS = [
    ToolSpec(
        name="bugbounty_comprehensive_assessment",
        mcp_tool_name="bugbounty_comprehensive_assessment",
        endpoint="/api/bugbounty/comprehensive-assessment",
        category="bug_bounty",
        description="Create comprehensive bug bounty assessment combining all specialized workflows.",
        params=[
            ParamSpec("domain", str, required=True, help_text="Target domain for bug bounty"),
            ParamSpec("scope", str, default="", help_text="Comma-separated list of in-scope domains/IPs"),
            ParamSpec(
                "priority_vulns", str, default="rce,sqli,xss,idor,ssrf",
                help_text="Comma-separated list of priority vulnerability types",
            ),
            ParamSpec("include_osint", bool, default=True, help_text="Include OSINT gathering workflow"),
            ParamSpec("include_business_logic", bool, default=True, help_text="Include business logic testing workflow"),
        ],
        handler=_comprehensive_assessment_handler,
    ),
    ToolSpec(
        name="bugbounty_authentication_bypass_testing",
        mcp_tool_name="bugbounty_authentication_bypass_testing",
        endpoint="/api/bugbounty/auth-bypass-testing",
        category="bug_bounty",
        description="Create authentication bypass testing workflow for bug bounty hunting.",
        params=[
            ParamSpec("target_url", str, required=True, help_text="Target URL with authentication"),
            ParamSpec("auth_type", str, default="form", help_text="Type of authentication (form, jwt, oauth, saml)"),
        ],
        handler=_auth_bypass_testing_handler,
    ),
    ToolSpec(
        name="bugbounty_reconnaissance_workflow",
        mcp_tool_name="bugbounty_reconnaissance_workflow",
        endpoint="/api/bugbounty/reconnaissance-workflow",
        category="bug_bounty",
        description="Create comprehensive reconnaissance workflow for bug bounty hunting.",
        params=[
            ParamSpec("domain", str, required=True, help_text="Target domain for bug bounty"),
            ParamSpec("scope", str, default="", help_text="Comma-separated list of in-scope domains/IPs"),
            ParamSpec("out_of_scope", str, default="", help_text="Comma-separated list of out-of-scope domains/IPs"),
            ParamSpec("program_type", str, default="web", help_text="Type of program (web, api, mobile, iot)"),
        ],
        handler=_reconnaissance_workflow_handler,
    ),
    ToolSpec(
        name="bugbounty_vulnerability_hunting",
        mcp_tool_name="bugbounty_vulnerability_hunting",
        endpoint="/api/bugbounty/vulnerability-hunting-workflow",
        category="bug_bounty",
        description="Create vulnerability hunting workflow prioritized by impact and bounty potential.",
        params=[
            ParamSpec("domain", str, required=True, help_text="Target domain for bug bounty"),
            ParamSpec(
                "priority_vulns", str, default="rce,sqli,xss,idor,ssrf",
                help_text="Comma-separated list of priority vulnerability types",
            ),
            ParamSpec("bounty_range", str, default="unknown", help_text="Expected bounty range (low, medium, high, critical)"),
        ],
        handler=_vulnerability_hunting_handler,
    ),
    ToolSpec(
        name="bugbounty_business_logic_testing",
        mcp_tool_name="bugbounty_business_logic_testing",
        endpoint="/api/bugbounty/business-logic-workflow",
        category="bug_bounty",
        description="Create business logic testing workflow for advanced bug bounty hunting.",
        params=[
            ParamSpec("domain", str, required=True, help_text="Target domain for bug bounty"),
            ParamSpec("program_type", str, default="web", help_text="Type of program (web, api, mobile)"),
        ],
        handler=_business_logic_workflow_handler,
    ),
    ToolSpec(
        name="bugbounty_osint_gathering",
        mcp_tool_name="bugbounty_osint_gathering",
        endpoint="/api/bugbounty/osint-workflow",
        category="bug_bounty",
        description="Create OSINT (Open Source Intelligence) gathering workflow for bug bounty reconnaissance.",
        params=[
            ParamSpec("domain", str, required=True, help_text="Target domain for OSINT gathering"),
        ],
        handler=_osint_workflow_handler,
    ),
    ToolSpec(
        name="bugbounty_file_upload_testing",
        mcp_tool_name="bugbounty_file_upload_testing",
        endpoint="/api/bugbounty/file-upload-testing",
        category="bug_bounty",
        description="Create file upload vulnerability testing workflow with bypass techniques.",
        params=[
            ParamSpec("target_url", str, required=True, help_text="Target URL with file upload functionality"),
        ],
        handler=_file_upload_testing_handler,
    ),
]

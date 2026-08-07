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


SPECS = [
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

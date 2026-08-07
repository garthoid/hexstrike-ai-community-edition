from datetime import datetime

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _ai_test_payload_command(p: dict) -> str:
    payload = p["payload"]
    target_url = p["target_url"]
    method = p["method"]

    if method.upper() == "GET":
        encoded_payload = payload.replace(" ", "%20").replace("'", "%27")
        return f"curl -s '{target_url}?test={encoded_payload}'"
    return f"curl -s -X POST -d 'test={payload}' '{target_url}'"


def _ai_test_payload_postprocess(raw: dict, p: dict) -> dict:
    payload = p["payload"]
    target_url = p["target_url"]
    method = p["method"]

    analysis = {
        "payload_tested": payload,
        "target_url": target_url,
        "method": method,
        "response_size": len(raw.get("stdout", "")),
        "success": raw.get("success", False),
        "potential_vulnerability": payload.lower() in raw.get("stdout", "").lower(),
        "recommendations": [
            "Analyze response for payload reflection",
            "Check for error messages indicating vulnerability",
            "Monitor application behavior changes",
        ],
    }

    return {
        "success": True,
        "test_result": raw,
        "ai_analysis": analysis,
        "timestamp": datetime.now().isoformat(),
    }


SPECS = [
    ToolSpec(
        name="ai_test_payload",
        mcp_tool_name="ai_test_payload",
        endpoint="/api/ai/test_payload",
        category="ai_payload",
        description="Test generated payload against target with AI analysis.",
        params=[
            ParamSpec("payload", str, required=True, help_text="The payload to test"),
            ParamSpec("target_url", str, required=True, help_text="Target URL to test against"),
            ParamSpec("method", str, default="GET", help_text="HTTP method (GET, POST)"),
        ],
        build_command=_ai_test_payload_command,
        postprocess=_ai_test_payload_postprocess,
        use_cache=False,
    ),
]

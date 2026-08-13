import logging
import time
from datetime import datetime

from backend.server_api.web_framework.browser_agent import browser_agent
from backend.server_core import ModernVisualEngine
from backend.server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError

logger = logging.getLogger(__name__)


def _browser_agent_handler(p: dict) -> dict:
    action = p["action"]
    url = p["url"]
    headless = p["headless"]
    wait_time = p["wait_time"]
    proxy_port = p.get("proxy_port") or None
    active_tests = p["active_tests"]

    logger.info(ModernVisualEngine.create_section_header("BROWSER AGENT", "🌐", "CRIMSON"))

    if action == "navigate":
        if not url:
            raise ToolValidationError("URL parameter is required for navigate action")

        if not browser_agent.driver:
            if not browser_agent.setup_browser(headless, proxy_port):
                raise RuntimeError("Failed to setup browser")

        result = browser_agent.navigate_and_inspect(url, wait_time)
        if result.get("success") and active_tests:
            active_results = browser_agent.run_active_tests(result.get("page_info", {}))
            result["active_tests"] = active_results
            if active_results["active_findings"]:
                logger.warning(ModernVisualEngine.format_error_card(
                    "WARNING", "BrowserAgent", f"Active findings: {len(active_results['active_findings'])}",
                ))
        return result

    elif action == "screenshot":
        if not browser_agent.driver:
            raise ToolValidationError("Browser not initialized. Use navigate action first.")

        screenshot_path = f"/tmp/security_screenshot_{int(time.time())}.png"
        browser_agent.driver.save_screenshot(screenshot_path)
        return {
            "success": True,
            "screenshot": screenshot_path,
            "current_url": browser_agent.driver.current_url,
            "timestamp": datetime.now().isoformat(),
        }

    elif action == "close":
        browser_agent.close_browser()
        return {"success": True, "message": "Browser closed successfully"}

    elif action == "status":
        return {
            "success": True,
            "browser_active": browser_agent.driver is not None,
            "screenshots_taken": len(browser_agent.screenshots),
            "pages_visited": len(browser_agent.page_sources),
        }

    raise ToolValidationError(f"Unknown action: {action}")


SPECS = [
    ToolSpec(
        name="browser_agent",
        mcp_tool_name="browser_agent_inspect",
        endpoint="/api/tools/browser-agent",
        category="web_framework",
        description="AI-powered browser agent for comprehensive web application inspection and security analysis.",
        params=[
            ParamSpec("url", str, default="", help_text="Target URL to inspect (required for the navigate action)"),
            ParamSpec("headless", bool, default=True, help_text="Run browser in headless mode"),
            ParamSpec("wait_time", int, default=5, help_text="Time to wait after page load, in seconds"),
            ParamSpec("action", str, default="navigate", help_text="Action to perform: navigate, screenshot, close, status"),
            ParamSpec("proxy_port", int, default=0, help_text="Optional proxy port for request interception (0 = none)"),
            ParamSpec("active_tests", bool, default=False, help_text="Run lightweight active reflected XSS tests (safe GET-only)"),
        ],
        handler=_browser_agent_handler,
    ),
]

import logging
import time

import backend.server_api.ops.system_monitoring as system_monitoring_api
import backend.server_core.config_core as config_core
from backend.server_core.singletons import cache, telemetry
from backend.server_core.tool_spec import ToolSpec

logger = logging.getLogger(__name__)


def _server_health_handler(p: dict) -> dict:
    tools_status = system_monitoring_api._get_tool_availability()

    essential_tools = system_monitoring_api.HEALTH_TOOL_CATEGORIES["essential"]
    all_essential_tools_available = all(tools_status.get(t, False) for t in essential_tools)

    category_stats = {
        cat: {
            "total": len(tools),
            "available": sum(1 for t in tools if tools_status.get(t, False)),
        }
        for cat, tools in system_monitoring_api.HEALTH_TOOL_CATEGORIES.items()
    }

    all_tools_count = len(tools_status)

    return {
        "status": "healthy",
        "message": "NyxStrike Tools API Server is operational",
        "version": config_core.get("VERSION", "unknown"),
        "tools_status": tools_status,
        "all_essential_tools_available": all_essential_tools_available,
        "total_tools_available": sum(1 for available in tools_status.values() if available),
        "total_tools_count": all_tools_count,
        "category_stats": category_stats,
        "plugin_install_hints": system_monitoring_api._get_plugin_install_hints(),
        "cache_stats": cache.get_stats(),
        "telemetry": telemetry.get_stats(),
        "uptime": time.time() - telemetry.stats["start_time"],
        "tool_availability_age_seconds": round(
            time.time() - system_monitoring_api._tool_availability_last_refresh, 1
        ),
    }


def _get_cache_stats_handler(p: dict) -> dict:
    return cache.get_stats()


def _clear_cache_handler(p: dict) -> dict:
    cache.clear()
    logger.info("Cache cleared")
    return {"success": True, "message": "Cache cleared"}


def _get_telemetry_handler(p: dict) -> dict:
    return telemetry.get_stats()


SPECS = [
    ToolSpec(
        name="server_health",
        mcp_tool_name="server_health",
        endpoint="/health",
        category="monitoring",
        description="Check the health status of the API server, including tool availability and telemetry.",
        method="GET",
        handler=_server_health_handler,
    ),
    ToolSpec(
        name="get_cache_stats",
        mcp_tool_name="get_cache_stats",
        endpoint="/api/cache/stats",
        category="monitoring",
        description="Get cache statistics from the API server.",
        method="GET",
        handler=_get_cache_stats_handler,
    ),
    ToolSpec(
        name="clear_cache",
        mcp_tool_name="clear_cache",
        endpoint="/api/cache/clear",
        category="monitoring",
        description="Clear the cache on the API server.",
        method="POST",
        handler=_clear_cache_handler,
    ),
    ToolSpec(
        name="get_telemetry",
        mcp_tool_name="get_telemetry",
        endpoint="/api/telemetry",
        category="monitoring",
        description="Get system telemetry from the API server.",
        method="GET",
        handler=_get_telemetry_handler,
    ),
]

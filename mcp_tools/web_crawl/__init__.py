from server_core.tool_specs.web_crawl import SPECS
from mcp_tools._generic.registrar import register_tool_from_spec


def register_web_crawl_tools(mcp, api_client, logger):
    for spec in SPECS:
        register_tool_from_spec(mcp, api_client, logger, spec)

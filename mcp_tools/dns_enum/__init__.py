from server_core.tool_specs.dns_enum import SPECS
from mcp_tools._generic.registrar import register_tool_from_spec


def register_dns_enum_tools(mcp, api_client, logger):
    for spec in SPECS:
        register_tool_from_spec(mcp, api_client, logger, spec)

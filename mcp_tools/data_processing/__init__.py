from server_core.tool_specs.data_processing import SPECS
from mcp_tools._generic.registrar import register_tool_from_spec


def register_data_processing_tools(mcp, api_client, logger):
    for spec in SPECS:
        register_tool_from_spec(mcp, api_client, logger, spec)

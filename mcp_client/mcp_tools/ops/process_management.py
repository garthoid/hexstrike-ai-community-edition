# mcp_tools/process_management.py
#
# Only execute_command lives here — the raw "run any shell command" backdoor.
# It stays hand-written on purpose: declaring it via ToolSpec wouldn't reduce
# risk, just relocate a dangerous passthrough. The other 6 process-management
# tools (list/status/terminate/pause/resume/dashboard) were migrated to
# backend/server_core/tool_specs/process_management.py.

from typing import Dict, Any
import asyncio

def register_process_management_tools(mcp, api_client, logger):
    @mcp.tool()
    async def execute_command(command: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Execute an arbitrary command on the API server with enhanced logging.

        Args:
            command: The command to execute
            use_cache: Whether to use caching for this command

        Returns:
            Command execution results with enhanced telemetry
        """
        try:
            logger.info(f"⚡ Executing command: {command}")
            result = api_client.execute_command(command, use_cache)
            if "error" in result:
                logger.error(f"❌ Command failed: {result['error']}")
                return {
                    "success": False,
                    "error": result["error"],
                    "stdout": "",
                    "stderr": f"Error executing command: {result['error']}"
                }

            if result.get("success"):
                execution_time = result.get("execution_time", 0)
                logger.info(f"✅ Command completed successfully in {execution_time:.2f}s")
            else:
                logger.warning(f"⚠️  Command completed with errors")

            return result
        except Exception as e:
            logger.error(f"💥 Error executing command '{command}': {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": f"Error executing command: {str(e)}"
            }

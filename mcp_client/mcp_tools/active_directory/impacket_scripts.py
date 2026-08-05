# mcp_tools/ad/impacket.py
import asyncio
from typing import Dict, Any, Optional

def register_impacket(mcp, api_client, logger, CliColors):
    """
    Register MCP tools for generic Impacket script execution.

    Expected backend endpoint:
      - POST /api/tool/active_directory/impacket/spec

    Note: the main "impacket_run" tool (POST /api/tool/active_directory/impacket)
    is registered declaratively via register_toolspec_category("active_directory").
    """

    async def _run_post(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, lambda: api_client.safe_post(endpoint, data)
        )

    @mcp.tool()
    async def impacket_get_spec(script: str) -> Dict[str, Any]:
        """
        Fetch the backend-discovered specification for an Impacket script.

        Useful for agents/UI logic to discover:
          - required positional arguments
          - supported options
          - usage string

        Args:
            script: Impacket script name without the 'impacket-' prefix

        Returns:
            Script specification from the backend
        """
        logger.info(
            f"{CliColors.FIRE_RED}📚 Fetching Impacket spec for: {script}{CliColors.RESET}"
        )

        result = await _run_post("api/tool/active_directory/impacket/spec", {"script": script})

        if result.get("error"):
            logger.error(
                f"{CliColors.ERROR}❌ Failed to fetch Impacket spec for {script}{CliColors.RESET}"
            )
        else:
            logger.info(
                f"{CliColors.SUCCESS}✅ Loaded Impacket spec for {script}{CliColors.RESET}"
            )

        return result

    @mcp.tool()
    async def impacket_ad_enum(
        script: str,
        target: str,
        dc_ip: str = "",
        username: str = "",
        password: str = "",
        hashes: str = "",
        kerberos: bool = False,
        no_pass: bool = False,
        aes_key: str = "",
        debug: bool = False,
        extra_options: Optional[Dict[str, Any]] = None,
        extra_args: str = "",
    ) -> Dict[str, Any]:
        """
        Convenience wrapper for common AD enumeration Impacket scripts.

        Supports scripts such as:
          - GetADUsers
          - GetADComputers
          - GetNPUsers
          - GetUserSPNs
          - GetLAPSPassword
          - findDelegation
          - lookupsid

        Args:
            script: Script name without 'impacket-' prefix
            target: Target string expected by the script
            dc_ip: Domain controller IP
            username: Optional username for scripts/agent formatting
            password: Optional password for scripts/agent formatting
            hashes: LM:NT hashes
            kerberos: Enable -k
            no_pass: Enable -no-pass
            aes_key: AES key for Kerberos auth
            debug: Enable -debug
            extra_options: Extra options dict merged into generated options
            extra_args: Raw extra CLI args for edge cases

        Returns:
            Execution result from backend
        """
        options: Dict[str, Any] = extra_options.copy() if extra_options else {}

        if dc_ip:
            options["dc-ip"] = dc_ip
        if hashes:
            options["hashes"] = hashes
        if kerberos:
            options["k"] = True
        if no_pass:
            options["no-pass"] = True
        if aes_key:
            options["aesKey"] = aes_key
        if debug:
            options["debug"] = True

        # username/password are not forced into options because most Impacket tools
        # usually expect them embedded in target; still passed through for agent context
        if username:
            options.setdefault("username", username)
        if password:
            options.setdefault("password", password)

        data: Dict[str, Any] = {
            "script": script,
            "target": target,
            "options": options,
            "extra_args": extra_args,
            "use_recovery": True,
        }

        logger.info(
            f"{CliColors.FIRE_RED}🕵️ Starting AD Impacket enumeration with {script} "
            f"against {target}{CliColors.RESET}"
        )

        result = await _run_post("api/tool/active_directory/impacket", data)

        if result.get("success"):
            logger.info(
                f"{CliColors.SUCCESS}✅ AD Impacket enumeration completed: {script}{CliColors.RESET}"
            )
        else:
            logger.error(
                f"{CliColors.ERROR}❌ AD Impacket enumeration failed: {script}{CliColors.RESET}"
            )

        return result

    @mcp.tool()
    async def impacket_remote_exec(
        script: str,
        target: str,
        command: str = "",
        hashes: str = "",
        kerberos: bool = False,
        no_pass: bool = False,
        aes_key: str = "",
        share: str = "",
        shell_type: str = "",
        debug: bool = False,
        extra_options: Optional[Dict[str, Any]] = None,
        extra_args: str = "",
    ) -> Dict[str, Any]:
        """
        Convenience wrapper for remote execution / interaction style scripts such as:
          - psexec
          - smbexec
          - wmiexec / wmiquery if added later
          - dcomexec
          - atexec
          - smbclient

        Args:
            script: Script name without 'impacket-' prefix
            target: Full target string
            command: Optional command to execute if supported by the script
            hashes: LM:NT hashes
            kerberos: Enable -k
            no_pass: Enable -no-pass
            aes_key: AES key for Kerberos auth
            share: SMB share if supported
            shell_type: Shell type if supported
            debug: Enable -debug
            extra_options: Additional options
            extra_args: Raw fallback args

        Returns:
            Execution result from backend
        """
        options: Dict[str, Any] = extra_options.copy() if extra_options else {}

        if hashes:
            options["hashes"] = hashes
        if kerberos:
            options["k"] = True
        if no_pass:
            options["no-pass"] = True
        if aes_key:
            options["aesKey"] = aes_key
        if share:
            options["share"] = share
        if shell_type:
            options["shell-type"] = shell_type
        if debug:
            options["debug"] = True

        if command:
            options["command"] = command

        data: Dict[str, Any] = {
            "script": script,
            "target": target,
            "options": options,
            "extra_args": extra_args,
            "use_recovery": True,
        }

        logger.info(
            f"{CliColors.FIRE_RED}⚔️ Starting remote Impacket action with {script} "
            f"against {target}{CliColors.RESET}"
        )

        result = await _run_post("api/tool/active_directory/impacket", data)

        if result.get("success"):
            logger.info(
                f"{CliColors.SUCCESS}✅ Remote Impacket action completed: {script}{CliColors.RESET}"
            )
        else:
            logger.error(
                f"{CliColors.ERROR}❌ Remote Impacket action failed: {script}{CliColors.RESET}"
            )

        return result
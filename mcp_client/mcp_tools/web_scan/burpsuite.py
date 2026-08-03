# mcp_tools/web_scan/burpsuite.py

from typing import Dict, Any
import asyncio


def register_burpsuite_tool(mcp, api_client, logger, CliColors):

    @mcp.tool()
    async def burpsuite_alternative_scan(target: str, scan_type: str = "comprehensive",
                                  headless: bool = True, max_depth: int = 3,
                                  max_pages: int = 50) -> Dict[str, Any]:
        """
        Comprehensive Burp Suite alternative combining HTTP framework and browser agent for complete web security testing.

        Args:
            target: Target URL or domain to scan
            scan_type: Type of scan (comprehensive, spider, passive, active)
            headless: Run browser in headless mode
            max_depth: Maximum crawling depth
            max_pages: Maximum pages to analyze

        Returns:
            Comprehensive security assessment results
        """
        data_payload = {
            "target": target,
            "scan_type": scan_type,
            "headless": headless,
            "max_depth": max_depth,
            "max_pages": max_pages
        }

        logger.info(f"{CliColors.BLOOD_RED}🔥 Starting Burp Suite Alternative {scan_type} scan: {target}{CliColors.RESET}")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, lambda: api_client.safe_post("api/tools/burpsuite-alternative", data_payload)
        )

        if result.get("success"):
            logger.info(f"{CliColors.SUCCESS}✅ Burp Suite Alternative scan completed for {target}{CliColors.RESET}")

            # Enhanced logging for comprehensive results
            if result.get("result", {}).get("summary"):
                summary = result["result"]["summary"]
                total_vulns = summary.get("total_vulnerabilities", 0)
                pages_analyzed = summary.get("pages_analyzed", 0)
                security_score = summary.get("security_score", 0)

                logger.info(f"{CliColors.HIGHLIGHT_BLUE} SCAN SUMMARY {CliColors.RESET}")
                logger.info(f"  📊 Pages Analyzed: {pages_analyzed}")
                logger.info(f"  🚨 Vulnerabilities: {total_vulns}")
                logger.info(f"  🛡️  Security Score: {security_score}/100")

                # Log vulnerability breakdown
                vuln_breakdown = summary.get("vulnerability_breakdown", {})
                for severity, count in vuln_breakdown.items():
                    if count > 0:
                        color = {
                                    'critical': CliColors.CRITICAL,
        'high': CliColors.FIRE_RED,
        'medium': CliColors.CYBER_ORANGE,
        'low': CliColors.YELLOW,
        'info': CliColors.INFO
    }.get(severity.lower(), CliColors.WHITE)

                        logger.info(f"  {color}{severity.upper()}: {count}{CliColors.RESET}")
        else:
            logger.error(f"{CliColors.ERROR}❌ Burp Suite Alternative scan failed for {target}{CliColors.RESET}")

        return result

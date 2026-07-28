from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _gospider_command(p: dict) -> str:
    if not p["version"] and not p["site"] and not p["sites"]:
        raise ToolValidationError("Provide either site or sites parameter")

    parts = ["gospider"]
    if p["site"]:
        parts.extend(["-s", p["site"]])
    if p["sites"]:
        parts.extend(["-S", p["sites"]])
    if p["proxy"]:
        parts.extend(["-p", p["proxy"]])
    if p["output"]:
        parts.extend(["-o", p["output"]])
    if p["user_agent"]:
        parts.extend(["-u", p["user_agent"]])
    if p["cookie"]:
        parts.extend(["--cookie", p["cookie"]])

    headers = p["headers"]
    if isinstance(headers, str) and headers:
        parts.extend(["-H", headers])
    elif isinstance(headers, list):
        for header in headers:
            if isinstance(header, str) and header:
                parts.extend(["-H", header])

    if p["burp"]:
        parts.extend(["--burp", p["burp"]])
    if p["blacklist"]:
        parts.extend(["--blacklist", p["blacklist"]])

    if p["threads"]:
        parts.extend(["-t", str(p["threads"])])
    if p["concurrent"]:
        parts.extend(["-c", str(p["concurrent"])])
    if p["depth"] is not None:
        parts.extend(["-d", str(p["depth"])])
    if p["delay"]:
        parts.extend(["-k", str(p["delay"])])
    if p["random_delay"]:
        parts.extend(["-K", str(p["random_delay"])])
    if p["timeout"]:
        parts.extend(["-m", str(p["timeout"])])

    if p["sitemap"]:
        parts.append("--sitemap")
    if p["robots"]:
        parts.append("--robots")
    if p["other_source"]:
        parts.append("-a")
    if p["include_subs"]:
        parts.append("-w")
    if p["include_other_source"]:
        parts.append("-r")
    if p["debug"]:
        parts.append("--debug")
    if p["verbose"]:
        parts.append("-v")
    if p["no_redirect"]:
        parts.append("--no-redirect")
    if p["version"]:
        parts.append("--version")

    if p["additional_args"]:
        parts.append(p["additional_args"])

    return " ".join(parts)


def _hakrawler_command(p: dict) -> str:
    command = f"echo '{p['url']}' | hakrawler -d {p['depth']}"
    if p["forms"]:
        command += " -s"
    if p["robots"] or p["sitemap"] or p["wayback"]:
        command += " -subs"
    command += " -u"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _katana_command(p: dict) -> str:
    command = f"katana -u {p['url']} -d {p['depth']}"
    if p["js_crawl"]:
        command += " -jc"
    if p["form_extraction"]:
        command += " -fx"
    if p["output_format"] == "json":
        command += " -jsonl"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


SPECS = [
    ToolSpec(
        name="gospider",
        mcp_tool_name="gospider_crawl",
        endpoint="/api/tools/gospider",
        category="web_crawl",
        description="Execute GoSpider web crawler.",
        params=[
            ParamSpec("site", str, default="", help_text="Single site to crawl"),
            ParamSpec("sites", str, default="", help_text="File path containing sites to crawl"),
            ParamSpec("proxy", str, default="", help_text="HTTP proxy URL"),
            ParamSpec("output", str, default="", help_text="Output folder path"),
            ParamSpec("user_agent", str, default="web", help_text="web, mobi, or custom UA string"),
            ParamSpec("cookie", str, default="", help_text="Cookie string"),
            ParamSpec("headers", list, default=[], help_text="Repeated request headers"),
            ParamSpec("burp", str, default="", help_text="Burp raw HTTP request file"),
            ParamSpec("blacklist", str, default="", help_text="URL blacklist regex"),
            ParamSpec("threads", int, default=1, help_text="Number of site threads"),
            ParamSpec("concurrent", int, default=5, help_text="Max concurrent requests per matching domain"),
            ParamSpec("depth", int, default=1, help_text="Max crawl depth (0 = infinite)"),
            ParamSpec("delay", int, default=0, help_text="Fixed delay between requests in seconds"),
            ParamSpec("random_delay", int, default=0, help_text="Extra randomized delay in seconds"),
            ParamSpec("timeout", int, default=10, help_text="Request timeout in seconds"),
            ParamSpec("sitemap", bool, default=False, help_text="Crawl sitemap.xml"),
            ParamSpec("robots", bool, default=True, help_text="Crawl robots.txt"),
            ParamSpec("other_source", bool, default=False, help_text="Include 3rd-party URL sources"),
            ParamSpec("include_subs", bool, default=False, help_text="Include subdomains from 3rd-party sources"),
            ParamSpec("include_other_source", bool, default=False, help_text="Include and crawl other-source URLs"),
            ParamSpec("debug", bool, default=False, help_text="Enable debug mode"),
            ParamSpec("verbose", bool, default=False, help_text="Enable verbose output"),
            ParamSpec("no_redirect", bool, default=False, help_text="Disable redirects"),
            ParamSpec("version", bool, default=False, help_text="Show version and exit"),
            ParamSpec("additional_args", str, default="", help_text="Additional GoSpider arguments"),
        ],
        build_command=_gospider_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="hakrawler",
        mcp_tool_name="hakrawler_crawl",
        endpoint="/api/tools/hakrawler",
        category="web_crawl",
        description="Execute Hakrawler for web endpoint discovery with enhanced logging.",
        params=[
            ParamSpec("url", str, required=True, help_text="Target URL to crawl"),
            ParamSpec("depth", int, default=2, help_text="Crawling depth (mapped to -d)"),
            ParamSpec("forms", bool, default=True, help_text="Include forms in crawling (mapped to -s)"),
            ParamSpec("robots", bool, default=True, help_text="Check robots.txt (mapped to -subs)"),
            ParamSpec("sitemap", bool, default=True, help_text="Check sitemap.xml (mapped to -subs)"),
            ParamSpec("wayback", bool, default=False, help_text="Use Wayback Machine (mapped to -subs)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Hakrawler arguments"),
        ],
        build_command=_hakrawler_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="katana",
        mcp_tool_name="katana_crawl",
        endpoint="/api/tools/katana",
        category="web_crawl",
        description="Execute Katana for next-generation crawling and spidering with enhanced logging.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL to crawl"),
            ParamSpec("depth", int, default=3, help_text="Crawling depth"),
            ParamSpec("js_crawl", bool, default=True, help_text="Enable JavaScript crawling"),
            ParamSpec("form_extraction", bool, default=True, help_text="Enable form extraction"),
            ParamSpec("output_format", str, default="json", help_text="Output format (json, txt)"),
            ParamSpec("additional_args", str, default="", help_text="Additional Katana arguments"),
        ],
        build_command=_katana_command,
        use_recovery=True,
    ),
]

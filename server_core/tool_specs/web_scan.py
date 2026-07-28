from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _bool(val) -> bool:
    """Coerce UI values to bool. Handles True/False, 'true'/'false', 1/0."""
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() == "true"
    return bool(val)


def _findings_as_success_postprocess(raw, params: dict) -> dict:
    if raw.get("return_code") == 1:
        raw["success"] = True
    return raw


def _breachsql_command(p: dict) -> str:
    command = f"breachsql -u {p['url']}"
    if p["data"]:
        command += f" -d {p['data']!r}"
    for header in (p["headers"] or {}).items():
        command += f" -H {header[0]}:{header[1]!r}"
    if p["cookies"]:
        command += f" -c {p['cookies']!r}"
    if p["proxy"]:
        command += f" --proxy {p['proxy']}"
    if p["threads"] and int(p["threads"]) != 5:
        command += f" -t {int(p['threads'])}"
    if p["timeout"] and int(p["timeout"]) != 15:
        command += f" --timeout {int(p['timeout'])}"
    if p["level"] and int(p["level"]) != 1:
        command += f" --level {int(p['level'])}"
    if p["dbms"] and p["dbms"] != "auto":
        command += f" --dbms {p['dbms']}"
    if p["technique"] and p["technique"] != "EBTUO":
        command += f" --technique {p['technique']}"
    if p["time_threshold"] and int(p["time_threshold"]) != 4:
        command += f" --time-threshold {int(p['time_threshold'])}"
    if p["risk"] and int(p["risk"]) != 1:
        command += f" --risk {int(p['risk'])}"
    if p["path_params"]:
        command += f" --path-params {','.join(p['path_params'])}"
    if p["cookie_params"]:
        command += f" --cookie-params {','.join(p['cookie_params'])}"
    if p["header_params"]:
        command += f" --header-params {','.join(p['header_params'])}"
    if _bool(p["exploit"]):
        command += " --exploit"
    if p["dump"]:
        command += f" --dump {p['dump']}"
    if _bool(p["dump_all"]):
        command += " --dump-all"
    if _bool(p["crawl"]):
        command += " --crawl"
    if p["max_pages"] and int(p["max_pages"]) != 100:
        command += f" --max-pages {int(p['max_pages'])}"
    if p["max_depth"] and int(p["max_depth"]) != 3:
        command += f" --max-depth {int(p['max_depth'])}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _dalfox_command(p: dict) -> str:
    url, pipe_mode = p["url"], p["pipe_mode"]
    if not url and not pipe_mode:
        raise ToolValidationError("URL parameter is required")

    command = "dalfox pipe" if pipe_mode else f"dalfox url {url}"
    if p["blind"]:
        command += " --blind"
    if p["mining_dom"]:
        command += " --dom"
    if p["mining_dict"]:
        command += " --mining-dict"
    if p["custom_payload"]:
        command += f" --custom-payload '{p['custom_payload']}'"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _interactsh_command(p: dict) -> str:
    command = f"interactsh-client -json -n {p['n']} -pi {p['poll_interval']}"
    if p["server"]:
        command += f" -server {p['server']}"
    if p["token"]:
        command += f" -token {p['token']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _jaeles_command(p: dict) -> str:
    command = f"jaeles scan -u {p['url']} -c {p['threads']} --timeout {p['timeout']}"
    if p["signatures"]:
        command += f" -s {p['signatures']}"
    if p["config"]:
        command += f" --config {p['config']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _joomscan_command(p: dict) -> str:
    command = f"joomscan --url {p['url']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _nikto_command(p: dict) -> str:
    command = f"nikto -h {p['target']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _phaseaccess_command(p: dict) -> str:
    command = f"phaseaccess -u {p['target']} --json -q"

    method = p["method"]
    if method and method != "GET":
        command += f" -X {method}"
    if p["body"]:
        command += f" -d {p['body']!r}"

    for key, val in (p["session_a_headers"] or {}).items():
        command += f" -H {key}:{val!r}"
    if p["session_a_cookies"]:
        command += f" -c {p['session_a_cookies']!r}"
    label_a = p["session_a_label"]
    if label_a and label_a != "session_a":
        command += f" --label-a {label_a}"

    for key, val in (p["session_b_headers"] or {}).items():
        command += f" --header-b {key}:{val!r}"
    if p["session_b_cookies"]:
        command += f" --cookie-b {p['session_b_cookies']!r}"
    if p["session_b_label"]:
        command += f" --label-b {p['session_b_label']}"

    if p["login_url"]:
        command += f" --login-url {p['login_url']}"
    if p["login_user"]:
        command += f" --login-user {p['login_user']!r}"
    if p["login_pass"]:
        command += f" --login-pass {p['login_pass']!r}"
    if p["login_user_field"]:
        command += f" --login-user-field {p['login_user_field']}"
    if p["login_pass_field"]:
        command += f" --login-pass-field {p['login_pass_field']}"

    if p["login_url_b"]:
        command += f" --login-url-b {p['login_url_b']}"
    if p["login_user_b"]:
        command += f" --login-user-b {p['login_user_b']!r}"
    if p["login_pass_b"]:
        command += f" --login-pass-b {p['login_pass_b']!r}"

    if _bool(p["crawl"]):
        command += " --crawl"
    if p["crawl_depth"] and int(p["crawl_depth"]) != 3:
        command += f" --crawl-depth {int(p['crawl_depth'])}"
    if p["crawl_pages"] and int(p["crawl_pages"]) != 100:
        command += f" --crawl-pages {int(p['crawl_pages'])}"
    if _bool(p["browser_crawl"]):
        command += " --browser-crawl"
    if _bool(p["auto_login"]):
        command += " --auto-login"

    if p["openapi"]:
        command += f" --openapi {p['openapi']}"
    if p["base_url"]:
        command += f" --base-url {p['base_url']}"
    if p["targets"]:
        command += f" --targets {p['targets']}"

    if p["chain_create"]:
        command += f" --chain-create {p['chain_create']}"
    if p["chain_body"]:
        command += f" --chain-body {p['chain_body']!r}"
    if p["chain_read"]:
        command += f" --chain-read {p['chain_read']}"

    if p["proxy"]:
        command += f" --proxy {p['proxy']}"
    if not _bool(p["verify_ssl"]):
        command += " --insecure"
    if p["delay"] and float(p["delay"]) > 0:
        command += f" --delay {float(p['delay'])}"
    if p["threads"] and int(p["threads"]) != 5:
        command += f" -t {int(p['threads'])}"
    if p["timeout"] and int(p["timeout"]) != 15:
        command += f" --timeout {int(p['timeout'])}"
    if p["user_agent"]:
        command += f" --user-agent {p['user_agent']!r}"

    if p["max_candidates"] and int(p["max_candidates"]) != 10:
        command += f" --max-candidates {int(p['max_candidates'])}"
    if p["min_confidence"]:
        command += f" --min-confidence {p['min_confidence']}"
    if not _bool(p["method_bypass"]):
        command += " --no-method-bypass"
    if not _bool(p["param_pollution"]):
        command += " --no-param-pollution"
    if not _bool(p["mass_assignment"]):
        command += " --no-mass-assignment"
    if not _bool(p["soft_delete"]):
        command += " --no-soft-delete"
    if not _bool(p["blind_idor"]):
        command += " --no-blind-idor"

    for extra_url in (p["extra_urls"] or []):
        command += f" --extra-url {extra_url}"

    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _sqlmap_command(p: dict) -> str:
    command = f"sqlmap -u {p['url']} --batch"
    if p["data"]:
        command += f' --data="{p["data"]}"'
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _stingxss_command(p: dict) -> str:
    command = f"stingxss -u {p['url']}"
    if p["data"]:
        command += f" -d {p['data']!r}"
    for key, val in (p["headers"] or {}).items():
        command += f" -H {key}:{val!r}"
    if p["cookies"]:
        command += f" -c {p['cookies']!r}"
    if p["proxy"]:
        command += f" --proxy {p['proxy']}"
    if p["threads"] and int(p["threads"]) != 5:
        command += f" -t {int(p['threads'])}"
    if p["timeout"] and int(p["timeout"]) != 15:
        command += f" --timeout {int(p['timeout'])}"
    if p["level"] and int(p["level"]) != 1:
        command += f" --level {int(p['level'])}"
    if _bool(p["crawl"]):
        command += " --crawl"
    if p["max_pages"] and int(p["max_pages"]) != 50:
        command += f" --max-pages {int(p['max_pages'])}"
    if p["max_depth"] and int(p["max_depth"]) != 3:
        command += f" --max-depth {int(p['max_depth'])}"
    if p["blind_callback"]:
        command += f" --blind {p['blind_callback']}"
    if _bool(p["browser"]):
        command += " --browser"
        if not _bool(p["browser_headless"]):
            command += " --no-browser-headless"
    if _bool(p["test_stored"]):
        command += " --test-stored"
    if _bool(p["poc"]):
        command += " --poc"
    for header in (p["inject_headers"] or []):
        command += f" --inject-headers {header}"
    # custom_payloads is a list — only supported via file; accepted but a no-op, matches Flask
    if not _bool(p["probe_filter"]):
        command += " --no-probe-filter"
    if _bool(p["graphql"]):
        command += " --graphql"
    if _bool(p["websocket"]):
        command += " --websocket"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _whatweb_command(p: dict) -> str:
    return f"whatweb -v -a 3 {p['url']}"


def _wpscan_command(p: dict) -> str:
    command = f"wpscan --url {p['url']}"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _xsser_command(p: dict) -> str:
    command = f"xsser --url '{p['url']}'"
    if p["params"]:
        command += f" --param='{p['params']}'"
    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


def _zap_command(p: dict) -> str:
    target, scan_type = p["target"], p["scan_type"]
    if not target and scan_type != "daemon":
        raise ToolValidationError("Target parameter is required for scans")

    if p["daemon"]:
        command = f"zaproxy -daemon -host {p['host']} -port {p['port']}"
        if p["api_key"]:
            command += f" -config api.key={p['api_key']}"
    else:
        command = f"zaproxy -cmd -quickurl {target}"
        if p["format"]:
            command += f" -quickout {p['format']}"
        if p["output_file"]:
            command += f' -quickprogress -dir "{p["output_file"]}"'
        if p["api_key"]:
            command += f" -config api.key={p['api_key']}"

    if p["additional_args"]:
        command += f" {p['additional_args']}"
    return command


SPECS = [
    ToolSpec(
        name="breachsql",
        mcp_tool_name="breachsql_scan",
        endpoint="/api/tools/breachsql",
        category="web_scan",
        description="Run BreachSQL SQL injection detection and exploitation.",
        params=[
            ParamSpec("url", str, required=True, help_text="Target URL (include the vulnerable parameter, e.g. /item?id=1)"),
            ParamSpec("data", str, default="", help_text="POST body (URL-encoded or JSON string)"),
            ParamSpec("headers", dict, default={}, help_text="Extra request headers as a dict"),
            ParamSpec("cookies", str, default="", help_text="Cookie header string"),
            ParamSpec("proxy", str, default="", help_text="HTTP proxy URL"),
            ParamSpec("threads", int, default=5, help_text="Concurrent threads (1-20)"),
            ParamSpec("timeout", int, default=15, help_text="Request timeout in seconds"),
            ParamSpec("level", int, default=1, help_text="Scan depth (1=params only, 2=+headers, 3=+cookies)"),
            ParamSpec("dbms", str, default="auto", help_text="Force backend (auto|mysql|mssql|postgres|sqlite|oracle)"),
            ParamSpec("technique", str, default="EBTUO", help_text="Detection techniques (letters: E=error B=boolean T=time U=union O=oob)"),
            ParamSpec("time_threshold", int, default=4, help_text="Seconds before a time-based injection is flagged"),
            ParamSpec("risk", int, default=1, help_text="Payload risk level (1-3)"),
            ParamSpec("path_params", list, default=[], help_text="Path segment names to inject (e.g. ['id'])"),
            ParamSpec("cookie_params", list, default=[], help_text="Cookie names to inject into"),
            ParamSpec("header_params", list, default=[], help_text="HTTP header names to inject into"),
            ParamSpec("exploit", bool, default=False, help_text="After detection, dump version/user/db/tables automatically"),
            ParamSpec("dump", str, default="", help_text="Table name to dump rows from"),
            ParamSpec("dump_all", bool, default=False, help_text="Dump every discovered table"),
            ParamSpec("crawl", bool, default=False, help_text="Crawl the site and test discovered endpoints"),
            ParamSpec("max_pages", int, default=100, help_text="Max pages to crawl"),
            ParamSpec("max_depth", int, default=3, help_text="Crawl depth limit"),
            ParamSpec("additional_args", str, default="", help_text="Additional BreachSQL arguments"),
        ],
        build_command=_breachsql_command,
        postprocess=_findings_as_success_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="dalfox",
        mcp_tool_name="dalfox_xss_scan",
        endpoint="/api/tools/dalfox",
        category="web_scan",
        description="Execute Dalfox for advanced XSS vulnerability scanning.",
        params=[
            ParamSpec("url", str, default="", help_text="The target URL"),
            ParamSpec("pipe_mode", bool, default=False, help_text="Use pipe mode for input"),
            ParamSpec("blind", bool, default=False, help_text="Enable blind XSS testing"),
            ParamSpec("mining_dom", bool, default=True, help_text="Enable DOM mining"),
            ParamSpec("mining_dict", bool, default=True, help_text="Enable dictionary mining"),
            ParamSpec("custom_payload", str, default="", help_text="Custom XSS payload"),
            ParamSpec("additional_args", str, default="", help_text="Additional Dalfox arguments"),
        ],
        build_command=_dalfox_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="interactsh",
        mcp_tool_name="interactsh_client",
        endpoint="/api/tools/web_scan/interactsh",
        category="web_scan",
        description="Run interactsh-client to generate OOB interaction URLs and capture out-of-band interactions.",
        params=[
            ParamSpec("server", str, default="", help_text="Custom interactsh server URL"),
            ParamSpec("token", str, default="", help_text="Authentication token for private server"),
            ParamSpec("n", int, default=1, help_text="Number of interaction payload URLs to generate"),
            ParamSpec("poll_interval", int, default=5, help_text="Polling interval in seconds between interaction checks"),
            ParamSpec("timeout", int, default=60, help_text="Total time in seconds to listen for interactions before exiting"),
            ParamSpec("additional_args", str, default="", help_text="Additional interactsh-client flags"),
        ],
        build_command=_interactsh_command,
        timeout_param="timeout",
        use_recovery=True,
    ),
    ToolSpec(
        name="jaeles",
        mcp_tool_name="jaeles_vulnerability_scan",
        endpoint="/api/tools/jaeles",
        category="web_scan",
        description="Execute Jaeles for advanced vulnerability scanning with custom signatures.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("signatures", str, default="", help_text="Custom signature path"),
            ParamSpec("config", str, default="", help_text="Configuration file"),
            ParamSpec("threads", int, default=20, help_text="Number of threads"),
            ParamSpec("timeout", int, default=20, help_text="Request timeout"),
            ParamSpec("additional_args", str, default="", help_text="Additional Jaeles arguments"),
        ],
        build_command=_jaeles_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="joomscan",
        mcp_tool_name="joomscan_analyze",
        endpoint="/api/tools/web_recon/joomscan",
        category="web_scan",
        description="Execute Joomscan for Joomla vulnerability scanning.",
        params=[
            ParamSpec("url", str, required=True, help_text="The Joomla site URL"),
            ParamSpec("additional_args", str, default="", help_text="Additional Joomscan arguments"),
        ],
        build_command=_joomscan_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="nikto",
        mcp_tool_name="nikto_scan",
        endpoint="/api/tools/nikto",
        category="web_scan",
        description="Execute Nikto web vulnerability scanner.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target URL or IP"),
            ParamSpec("additional_args", str, default="", help_text="Additional Nikto arguments"),
        ],
        build_command=_nikto_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="phaseaccess",
        mcp_tool_name="phaseaccess_scan",
        endpoint="/api/tools/phaseaccess",
        category="web_scan",
        description="Run PhaseAccess IDOR/BOLA scanner.",
        params=[
            ParamSpec("target", str, required=True, help_text="Primary target URL (e.g. http://app.example.invalid/users/42)"),
            ParamSpec("session_a_headers", dict, default={}, help_text="Auth headers for session A"),
            ParamSpec("session_a_cookies", str, default="", help_text="Cookie string for session A"),
            ParamSpec("session_a_label", str, default="session_a", help_text="Human label for session A shown in findings"),
            ParamSpec("session_b_headers", dict, default={}, help_text="Auth headers for session B — enables dual-session mode"),
            ParamSpec("session_b_cookies", str, default="", help_text="Cookie string for session B"),
            ParamSpec("session_b_label", str, default="", help_text="Label for session B — leave empty for single-session"),
            ParamSpec("method", str, default="GET", help_text="HTTP method for the primary target"),
            ParamSpec("body", str, default="", help_text="Request body for POST/PUT endpoints"),
            ParamSpec("login_url", str, default="", help_text="Login form URL to authenticate session A"),
            ParamSpec("login_user", str, default="", help_text="Username for session A form login"),
            ParamSpec("login_pass", str, default="", help_text="Password for session A form login"),
            ParamSpec("login_user_field", str, default="", help_text="Form field name for the username"),
            ParamSpec("login_pass_field", str, default="", help_text="Form field name for the password"),
            ParamSpec("login_url_b", str, default="", help_text="Login form URL for session B"),
            ParamSpec("login_user_b", str, default="", help_text="Username for session B form login"),
            ParamSpec("login_pass_b", str, default="", help_text="Password for session B form login"),
            ParamSpec("crawl", bool, default=False, help_text="Crawl target before scanning to auto-discover endpoints"),
            ParamSpec("crawl_depth", int, default=3, help_text="Crawler max depth"),
            ParamSpec("crawl_pages", int, default=100, help_text="Crawler max pages"),
            ParamSpec("browser_crawl", bool, default=False, help_text="Use headless Chromium for JS-rendered SPA discovery"),
            ParamSpec("auto_login", bool, default=False, help_text="Auto-discover login endpoints during crawl and authenticate both sessions"),
            ParamSpec("openapi", str, default="", help_text="OpenAPI/Swagger spec path or URL"),
            ParamSpec("base_url", str, default="", help_text="Base URL override for OpenAPI spec"),
            ParamSpec("targets", str, default="", help_text="Import endpoints from a HAR file or Burp Suite XML export"),
            ParamSpec("chain_create", str, default="", help_text="Stored IDOR create endpoint, format METHOD:URL"),
            ParamSpec("chain_body", str, default="", help_text="Request body for --chain-create"),
            ParamSpec("chain_read", str, default="", help_text="Stored IDOR read URL template"),
            ParamSpec("proxy", str, default="", help_text="HTTP proxy URL"),
            ParamSpec("verify_ssl", bool, default=True, help_text="Verify TLS certificates"),
            ParamSpec("delay", float, default=0.0, help_text="Seconds between requests"),
            ParamSpec("threads", int, default=5, help_text="Concurrent request threads"),
            ParamSpec("timeout", int, default=15, help_text="Request timeout in seconds"),
            ParamSpec("user_agent", str, default="", help_text="Override User-Agent"),
            ParamSpec("max_candidates", int, default=10, help_text="Max tamper candidates per discovered ID parameter"),
            ParamSpec("min_confidence", str, default="", help_text="Minimum confidence to report (confirmed|high|medium|low|info)"),
            ParamSpec("method_bypass", bool, default=True, help_text="Test HTTP method bypass variants"),
            ParamSpec("param_pollution", bool, default=True, help_text="Test HTTP parameter pollution"),
            ParamSpec("mass_assignment", bool, default=True, help_text="Test mass assignment on JSON body endpoints"),
            ParamSpec("soft_delete", bool, default=True, help_text="Test soft-delete bypass via hint parameters"),
            ParamSpec("blind_idor", bool, default=True, help_text="Flag blind IDOR via status-only signals"),
            ParamSpec("extra_urls", list, default=[], help_text="Additional URLs to test alongside the primary target"),
            ParamSpec("additional_args", str, default="", help_text="Additional PhaseAccess arguments"),
        ],
        build_command=_phaseaccess_command,
        postprocess=_findings_as_success_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="sqlmap",
        mcp_tool_name="sqlmap_scan",
        endpoint="/api/tools/sqlmap",
        category="web_scan",
        description="Execute SQLMap for SQL injection testing.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("data", str, default="", help_text="POST data for testing"),
            ParamSpec("additional_args", str, default="", help_text="Additional SQLMap arguments"),
        ],
        build_command=_sqlmap_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="stingxss",
        mcp_tool_name="stingxss_scan",
        endpoint="/api/tools/stingxss",
        category="web_scan",
        description="Run StingXSS context-aware XSS scanner.",
        params=[
            ParamSpec("url", str, required=True, help_text="Target URL"),
            ParamSpec("data", str, default="", help_text="POST body for form/API endpoints"),
            ParamSpec("headers", dict, default={}, help_text="Extra request headers"),
            ParamSpec("cookies", str, default="", help_text="Cookie header string"),
            ParamSpec("proxy", str, default="", help_text="HTTP proxy URL"),
            ParamSpec("threads", int, default=5, help_text="Concurrent threads (1-20)"),
            ParamSpec("timeout", int, default=15, help_text="Request timeout in seconds"),
            ParamSpec("level", int, default=1, help_text="Scan depth (1=query params, 2=+headers, 3=+cookies)"),
            ParamSpec("crawl", bool, default=False, help_text="Crawl the site and test all discovered endpoints"),
            ParamSpec("max_pages", int, default=50, help_text="Max pages to crawl"),
            ParamSpec("max_depth", int, default=3, help_text="Crawl depth limit"),
            ParamSpec("blind_callback", str, default="", help_text="OOB callback URL for blind XSS"),
            ParamSpec("browser", bool, default=False, help_text="Confirm XSS execution via headless Chromium"),
            ParamSpec("browser_headless", bool, default=True, help_text="Run browser in headless mode"),
            ParamSpec("test_stored", bool, default=False, help_text="Attempt stored XSS detection"),
            ParamSpec("poc", bool, default=False, help_text="Generate ready-to-use PoC payloads for confirmed findings"),
            ParamSpec("inject_headers", list, default=[], help_text="HTTP header names to inject into"),
            ParamSpec("custom_payloads", list, default=[], help_text="Additional payloads (accepted, list form currently unsupported server-side)"),
            ParamSpec("probe_filter", bool, default=True, help_text="Pre-probe each parameter to filter unusable payloads"),
            ParamSpec("graphql", bool, default=False, help_text="Test GraphQL endpoints discovered or specified"),
            ParamSpec("websocket", bool, default=False, help_text="Test WebSocket endpoints"),
            ParamSpec("additional_args", str, default="", help_text="Additional StingXSS arguments"),
        ],
        build_command=_stingxss_command,
        postprocess=_findings_as_success_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="whatweb",
        mcp_tool_name="whatweb_analyze",
        endpoint="/api/tools/web_recon/whatweb",
        category="web_scan",
        description="Execute WhatWeb for web technology fingerprinting.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target website URL"),
        ],
        build_command=_whatweb_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="wpscan",
        mcp_tool_name="wpscan_analyze",
        endpoint="/api/tools/wpscan",
        category="web_scan",
        description="Execute WPScan for WordPress vulnerability scanning.",
        params=[
            ParamSpec("url", str, required=True, help_text="The WordPress site URL"),
            ParamSpec("additional_args", str, default="", help_text="Additional WPScan arguments"),
        ],
        build_command=_wpscan_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="xsser",
        mcp_tool_name="xsser_scan",
        endpoint="/api/tools/xsser",
        category="web_scan",
        description="Execute XSSer for XSS vulnerability testing.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("params", str, default="", help_text="Parameters to test"),
            ParamSpec("additional_args", str, default="", help_text="Additional XSSer arguments"),
        ],
        build_command=_xsser_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="zap",
        mcp_tool_name="zap_scan",
        endpoint="/api/tools/zap",
        category="web_scan",
        description="Execute OWASP ZAP.",
        params=[
            ParamSpec("target", str, default="", help_text="Target URL"),
            ParamSpec("scan_type", str, default="baseline", help_text="Type of scan (baseline, full, api)"),
            ParamSpec("api_key", str, default="", help_text="ZAP API key"),
            ParamSpec("daemon", bool, default=False, help_text="Run in daemon mode"),
            ParamSpec("port", str, default="8090", help_text="Port for ZAP daemon"),
            ParamSpec("host", str, default="0.0.0.0", help_text="Host for ZAP daemon"),
            ParamSpec("format", str, default="xml", help_text="Output format (xml, json, html)"),
            ParamSpec("output_file", str, default="", help_text="Output file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional ZAP arguments"),
        ],
        build_command=_zap_command,
        use_recovery=True,
    ),
]

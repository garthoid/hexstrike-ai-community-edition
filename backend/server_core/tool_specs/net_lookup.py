import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec

_RECORD_TYPES = ["A", "MX", "NS", "TXT"]


def _whois_command(p: dict) -> str:
    return shlex.join(["whois", p["target"]])


def _whois_postprocess(raw: dict, params: dict) -> dict:
    output = raw.get("stdout") or raw.get("stderr") or ""
    return {"success": raw.get("success", False), "output": output}


def _http_headers_command(p: dict) -> str:
    scheme = "https" if p["https"] else "http"
    clean = p["target"].replace("https://", "").replace("http://", "")
    url = f"{scheme}://{clean}"
    argv = ["curl", "-sI", "-k", "--max-time", str(int(p["timeout"]))]
    if p["follow_redirects"]:
        argv.append("--location")
    argv.append(url)
    p["_url"] = url
    return shlex.join(argv)


def _parse_headers(raw: str) -> tuple:
    """Parse raw `curl -I` output into (headers_dict, status_line), keeping the
    last response block when redirects produce multiple blocks."""
    blocks = []
    current: list = []
    for line in raw.splitlines():
        if line.strip() == "" and current:
            blocks.append(current)
            current = []
        else:
            current.append(line)
    if current:
        blocks.append(current)

    block = blocks[-1] if blocks else []
    status_line = block[0].strip() if block else ""
    headers: dict = {}
    for line in block[1:]:
        if ":" in line:
            name, _, value = line.partition(":")
            headers[name.strip()] = value.strip()
    return headers, status_line


def _http_headers_postprocess(raw: dict, params: dict) -> dict:
    success = raw.get("success", False)
    output = raw.get("stdout", "") or ""
    if not success and raw.get("stderr"):
        output = output + raw.get("stderr", "")
    headers, status_line = _parse_headers(output)
    return {
        "success": success,
        "output": output,
        "headers": headers,
        "status_line": status_line,
        "target": params["_url"],
    }


def _dig_commands(p: dict) -> list:
    requested = p["record_types"]
    types = [r.upper() for r in requested if r.upper() in _RECORD_TYPES] or list(_RECORD_TYPES)
    p["_record_types_used"] = types
    return [shlex.join(["dig", "+short", rtype, p["target"]]) for rtype in types]


def _dig_postprocess(raw_list: list, params: dict) -> dict:
    records = {}
    sections = []
    for rtype, raw in zip(params["_record_types_used"], raw_list):
        output = (raw.get("stdout") or "").strip()
        if not output and (raw.get("stderr") or "").strip():
            output = raw.get("stderr", "").strip()
        records[rtype] = output
        sections.append(f"[{rtype} Records]\n{output}")
    return {
        "success": True,
        "target": params["target"],
        "records": records,
        "output": "\n\n".join(sections),
    }


SPECS = [
    ToolSpec(
        name="whois",
        mcp_tool_name="whois_lookup",
        endpoint="/api/tools/whois",
        category="net_lookup",
        description="Perform a WHOIS lookup for a domain or IP address.",
        params=[
            ParamSpec("target", str, required=True, help_text="The domain or IP to query"),
        ],
        build_command=_whois_command,
        postprocess=_whois_postprocess,
        use_cache=False,
        timeout=30,
        use_recovery=True,
    ),
    ToolSpec(
        name="http-headers",
        mcp_tool_name="check_http_headers",
        endpoint="/api/tools/http-headers",
        category="net_lookup",
        description="Fetch HTTP response headers for a target using curl -sI.",
        params=[
            ParamSpec("target", str, required=True, help_text="Hostname, IP, or URL"),
            ParamSpec("https", bool, default=False, help_text="Probe https:// instead of http://"),
            ParamSpec("follow_redirects", bool, default=True, help_text="Follow HTTP redirects"),
            ParamSpec("timeout", int, default=10, help_text="curl --max-time in seconds"),
        ],
        build_command=_http_headers_command,
        postprocess=_http_headers_postprocess,
        use_cache=False,
        use_recovery=True,
    ),
    ToolSpec(
        name="dig",
        mcp_tool_name="dig_dns",
        endpoint="/api/tools/dig",
        category="net_lookup",
        description="DNS record lookup using dig +short. Queries A, MX, NS, and TXT records by default.",
        params=[
            ParamSpec("target", str, required=True, help_text="Domain name to query"),
            ParamSpec("record_types", list, default=["A", "MX", "NS", "TXT"], help_text="Record types to query"),
            ParamSpec("timeout", int, default=15, help_text="Per-query timeout in seconds"),
        ],
        build_command=_dig_commands,
        postprocess=_dig_postprocess,
        use_cache=False,
        use_recovery=True,
    ),
]

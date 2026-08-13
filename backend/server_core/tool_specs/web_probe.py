import os
import re
import shlex
import shutil
from urllib.parse import urlparse

from backend.server_core import config_core
from backend.server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _httpx_command(p: dict) -> str:
    home_path = os.path.expanduser("~")
    binary_overrides = config_core.get("BINARY_PATH_OVERRIDES", {})
    httpx_bin_template = binary_overrides.get("httpx", "")
    httpx_bin = httpx_bin_template.replace("{HOME}", home_path) if httpx_bin_template else "httpx"

    argv = [httpx_bin, "-u", p["target"], "-t", str(p["threads"])]
    if p["probe"]:
        argv.append("-probe")
    if p["tech_detect"]:
        argv.append("-tech-detect")
    if p["status_code"]:
        argv.append("-sc")
    if p["content_length"]:
        argv.append("-cl")
    if p["title"]:
        argv.append("-title")
    if p["web_server"]:
        argv.append("-server")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _append_value(args, flag, value):
    if value not in ("", None):
        args.extend([flag, str(value)])


def _append_bool(args, enabled, flag):
    if enabled:
        args.append(flag)


def _testssl_command(p: dict) -> str:
    target = str(p["target"]).strip()
    help_mode = p["help_mode"]
    banner = p["banner"]
    version = p["version"]
    local_mode = p["local_mode"]
    local_pattern = str(p["local_pattern"]).strip()

    standalone_count = sum([
        bool(help_mode),
        bool(banner),
        bool(version),
        bool(local_mode or local_pattern),
    ])

    if standalone_count > 1:
        raise ToolValidationError("Only one standalone mode may be used at a time")
    if standalone_count and target:
        raise ToolValidationError("Standalone modes cannot be combined with a target URI")

    file_input = str(p["file_input"]).strip()
    mx = str(p["mx"]).strip()

    if not standalone_count and not target and not file_input and not mx:
        raise ToolValidationError("Target is required unless using a standalone mode, --file, or --mx")

    valid_modes = {"serial", "parallel"}
    valid_warnings = {"", "batch", "off"}
    valid_nodns = {"", "min", "none"}
    valid_mapping = {"", "openssl", "iana", "rfc", "no-openssl", "no-iana", "no-rfc"}
    valid_severity = {"", "LOW", "MEDIUM", "HIGH", "CRITICAL"}

    mode = str(p["mode"]).strip()
    warnings = str(p["warnings"]).strip()
    nodns = str(p["nodns"]).strip()
    mapping = str(p["mapping"]).strip()
    severity = str(p["severity"]).strip().upper()

    if mode not in valid_modes:
        raise ToolValidationError("mode must be one of: serial, parallel")
    if warnings not in valid_warnings:
        raise ToolValidationError("warnings must be one of: batch, off")
    if nodns not in valid_nodns:
        raise ToolValidationError("nodns must be one of: min, none")
    if mapping not in valid_mapping:
        raise ToolValidationError("mapping must be one of: openssl, iana, rfc, no-openssl, no-iana, no-rfc")
    if severity not in valid_severity:
        raise ToolValidationError("severity must be one of: LOW, MEDIUM, HIGH, CRITICAL")

    color = p["color"]
    debug = p["debug"]
    socket_timeout = p["socket_timeout"]
    openssl_timeout = p["openssl_timeout"]

    if color not in (0, 1, 2, 3):
        raise ToolValidationError("color must be one of: 0, 1, 2, 3")
    if not isinstance(debug, int) or debug < 0 or debug > 6:
        raise ToolValidationError("debug must be an integer between 0 and 6")
    if not isinstance(socket_timeout, int) or socket_timeout < 0:
        raise ToolValidationError("socket_timeout must be a non-negative integer")
    if not isinstance(openssl_timeout, int) or openssl_timeout < 0:
        raise ToolValidationError("openssl_timeout must be a non-negative integer")

    testssl_executable = shutil.which("testssl") or shutil.which("testssl.sh")
    if not testssl_executable:
        raise ToolValidationError("testssl tool not found")

    args = [testssl_executable]

    if help_mode:
        args.append("--help")
    elif banner:
        args.append("--banner")
    elif version:
        args.append("--version")
    elif local_mode or local_pattern:
        args.append("--local")
        if local_pattern:
            args.append(local_pattern)
    else:
        _append_value(args, "--starttls", str(p["starttls"]).strip())
        _append_value(args, "--xmpphost", str(p["xmpphost"]).strip())
        _append_value(args, "--mx", mx)
        _append_value(args, "--file", file_input)
        _append_value(args, "--mode", mode)
        _append_value(args, "--warnings", warnings)
        if socket_timeout:
            _append_value(args, "--socket-timeout", socket_timeout)
        if openssl_timeout:
            _append_value(args, "--openssl-timeout", openssl_timeout)

        _append_bool(args, p["each_cipher"], "--each-cipher")
        _append_bool(args, p["cipher_per_proto"], "--cipher-per-proto")
        _append_bool(args, p["categories"], "--std")
        _append_bool(args, p["forward_secrecy"], "--forward-secrecy")
        _append_bool(args, p["protocols"], "--protocols")
        _append_bool(args, p["grease"], "--grease")
        _append_bool(args, p["server_defaults"], "--server-defaults")
        _append_bool(args, p["server_preference"], "--server-preference")
        _append_value(args, "--single-cipher", str(p["single_cipher"]).strip())
        _append_bool(args, p["client_simulation"], "--client-simulation")
        _append_bool(args, p["headers"], "--headers")
        _append_bool(args, p["vulnerable"], "--vulnerable")

        _append_bool(args, p["full"], "--full")
        _append_bool(args, p["bugs"], "--bugs")
        _append_bool(args, p["assume_http"], "--assume-http")
        _append_bool(args, p["ssl_native"], "--ssl-native")
        _append_value(args, "--openssl", str(p["openssl_path"]).strip())
        _append_value(args, "--proxy", str(p["proxy"]).strip())
        _append_bool(args, p["ipv4_only"], "-4")
        _append_bool(args, p["ipv6_only"], "-6")
        _append_value(args, "--ip", str(p["ip"]).strip())
        _append_value(args, "--nodns", nodns)
        _append_bool(args, p["sneaky"], "--sneaky")
        _append_value(args, "--user-agent", str(p["user_agent"]).strip())
        _append_bool(args, p["ids_friendly"], "--ids-friendly")
        _append_bool(args, p["phone_out"], "--phone-out")
        _append_value(args, "--add-ca", str(p["add_ca"]).strip())
        _append_value(args, "--mtls", str(p["mtls"]).strip())
        _append_value(args, "--basicauth", str(p["basicauth"]).strip())
        _append_value(args, "--reqheader", str(p["reqheader"]).strip())
        _append_bool(args, p["rating_only"], "--rating-only")

        _append_bool(args, p["quiet"], "--quiet")
        _append_bool(args, p["wide"], "--wide")
        _append_bool(args, p["show_each"], "--show-each")
        _append_value(args, "--mapping", mapping)
        _append_value(args, "--color", color)
        _append_bool(args, p["colorblind"], "--colorblind")
        if debug:
            _append_value(args, "--debug", debug)
        _append_bool(args, p["disable_rating"], "--disable-rating")

        _append_value(args, "--logfile", str(p["logfile"]).strip())
        _append_bool(args, p["json_output"], "--json")
        _append_value(args, "--jsonfile", str(p["jsonfile"]).strip())
        _append_bool(args, p["json_pretty"], "--json-pretty")
        _append_value(args, "--jsonfile-pretty", str(p["jsonfile_pretty"]).strip())
        _append_bool(args, p["csv_output"], "--csv")
        _append_value(args, "--csvfile", str(p["csvfile"]).strip())
        _append_bool(args, p["html_output"], "--html")
        _append_value(args, "--htmlfile", str(p["htmlfile"]).strip())
        _append_value(args, "--outfile", str(p["outfile"]).strip())
        _append_bool(args, p["hints"], "--hints")
        _append_value(args, "--severity", severity)
        _append_bool(args, p["append"], "--append")
        _append_bool(args, p["overwrite"], "--overwrite")
        _append_value(args, "--outprefix", str(p["outprefix"]).strip())

        additional_args = str(p["additional_args"]).strip()
        if additional_args:
            args.extend(shlex.split(additional_args))

        if target:
            parsed_target = urlparse(target)
            args.append(parsed_target.netloc if parsed_target.netloc else target)

    return " ".join(shlex.quote(arg) for arg in args)


_ALLOWED_EXTRA_FLAGS = {
    "limit": ("-l", False),
    "timeout": ("-t", False),
    "verbose": ("-v", True),
    "no_subs": ("-subs", True),
}
_VALID_MODES = {"U", "R", "B"}
_DOMAIN_RE = re.compile(r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$")


def _validate_waymore_input(value: str) -> bool:
    parsed = urlparse(value)
    if parsed.scheme in ("http", "https"):
        return bool(parsed.netloc) and not parsed.path.startswith("/..")
    return bool(_DOMAIN_RE.match(value))


def _waymore_command(p: dict) -> str:
    input_value = p["input"]
    mode = p["mode"]

    if not _validate_waymore_input(input_value):
        raise ToolValidationError("Invalid input: must be a valid URL or domain")
    if mode not in _VALID_MODES:
        raise ToolValidationError(f"Invalid mode: must be one of {sorted(_VALID_MODES)}")

    cmd = ["waymore", "-i", input_value, "-mode", mode]
    if p["output_urls"]:
        cmd.extend(["-oU", p["output_urls"]])
    if p["output_responses"]:
        cmd.extend(["-oR", p["output_responses"]])

    for key, (flag, is_bool) in _ALLOWED_EXTRA_FLAGS.items():
        value = p.get(key)
        if is_bool:
            if value:
                cmd.append(flag)
        elif value:
            cmd.extend([flag, str(value)])

    return " ".join(shlex.quote(arg) for arg in cmd)


SPECS = [
    ToolSpec(
        name="httpx",
        mcp_tool_name="httpx_probe",
        endpoint="/api/tools/httpx",
        category="web_probe",
        description="Execute httpx for fast HTTP probing and technology detection.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target file or single URL"),
            ParamSpec("probe", bool, default=True, help_text="Enable probing"),
            ParamSpec("tech_detect", bool, default=False, help_text="Enable technology detection"),
            ParamSpec("status_code", bool, default=False, help_text="Show status codes"),
            ParamSpec("content_length", bool, default=False, help_text="Show content length"),
            ParamSpec("title", bool, default=False, help_text="Show page titles"),
            ParamSpec("web_server", bool, default=False, help_text="Show web server"),
            ParamSpec("threads", int, default=50, help_text="Number of threads"),
            ParamSpec("additional_args", str, default="", help_text="Additional httpx arguments"),
        ],
        build_command=_httpx_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="testssl",
        mcp_tool_name="testssl_analyze",
        endpoint="/api/tools/testssl",
        category="web_probe",
        description="Execute testssl.sh for TLS/SSL analysis.",
        params=[
            ParamSpec("target", str, default="", help_text="host|host:port|URL|URL:port. Required unless using a standalone mode"),
            ParamSpec("help_mode", bool, default=False, help_text="Standalone: show help"),
            ParamSpec("banner", bool, default=False, help_text="Standalone: show banner"),
            ParamSpec("version", bool, default=False, help_text="Standalone: show version"),
            ParamSpec("local_mode", bool, default=False, help_text="Standalone: local mode"),
            ParamSpec("local_pattern", str, default="", help_text="Standalone: local mode pattern"),
            ParamSpec("starttls", str, default="", help_text="STARTTLS protocol"),
            ParamSpec("xmpphost", str, default="", help_text="XMPP host"),
            ParamSpec("mx", str, default="", help_text="Test all MX records of a domain"),
            ParamSpec("file_input", str, default="", help_text="Read commands from a file"),
            ParamSpec("mode", str, default="serial", help_text="serial or parallel"),
            ParamSpec("warnings", str, default="", help_text="batch or off"),
            ParamSpec("socket_timeout", int, default=0, help_text="Socket timeout in seconds"),
            ParamSpec("openssl_timeout", int, default=0, help_text="OpenSSL timeout in seconds"),
            ParamSpec("each_cipher", bool, default=False, help_text="Test each local cipher remotely"),
            ParamSpec("cipher_per_proto", bool, default=False, help_text="Check each local cipher per protocol"),
            ParamSpec("categories", bool, default=False, help_text="Run standard checks (--std)"),
            ParamSpec("forward_secrecy", bool, default=False, help_text="Check forward secrecy ciphers"),
            ParamSpec("protocols", bool, default=True, help_text="Check TLS/SSL protocols"),
            ParamSpec("grease", bool, default=False, help_text="Check GREASE extension"),
            ParamSpec("server_defaults", bool, default=True, help_text="Display server default picks"),
            ParamSpec("server_preference", bool, default=False, help_text="Display server cipher preferences"),
            ParamSpec("single_cipher", str, default="", help_text="Test a single cipher"),
            ParamSpec("client_simulation", bool, default=False, help_text="Simulate common clients"),
            ParamSpec("headers", bool, default=False, help_text="Check HTTP security headers"),
            ParamSpec("vulnerable", bool, default=False, help_text="Check known vulnerabilities"),
            ParamSpec("full", bool, default=False, help_text="Run all checks"),
            ParamSpec("bugs", bool, default=False, help_text="Enable workaround for buggy servers"),
            ParamSpec("assume_http", bool, default=False, help_text="Assume HTTP even if unsure"),
            ParamSpec("ssl_native", bool, default=False, help_text="Use OpenSSL for connections"),
            ParamSpec("openssl_path", str, default="", help_text="Path to openssl binary"),
            ParamSpec("proxy", str, default="", help_text="SOCKS/HTTP proxy"),
            ParamSpec("ipv4_only", bool, default=False, help_text="Force IPv4 only"),
            ParamSpec("ipv6_only", bool, default=False, help_text="Force IPv6 only"),
            ParamSpec("ip", str, default="", help_text="Force IP address to connect to"),
            ParamSpec("nodns", str, default="", help_text="min or none"),
            ParamSpec("sneaky", bool, default=False, help_text="Use a common user agent"),
            ParamSpec("user_agent", str, default="", help_text="Custom user agent string"),
            ParamSpec("ids_friendly", bool, default=False, help_text="Avoid triggering IDS/IPS"),
            ParamSpec("phone_out", bool, default=False, help_text="Allow outgoing connections to check revocation"),
            ParamSpec("add_ca", str, default="", help_text="Path to an additional CA file"),
            ParamSpec("mtls", str, default="", help_text="Client certificate for mutual TLS"),
            ParamSpec("basicauth", str, default="", help_text="user:pass for HTTP basic auth"),
            ParamSpec("reqheader", str, default="", help_text="Additional HTTP request header"),
            ParamSpec("rating_only", bool, default=False, help_text="Display only rating information"),
            ParamSpec("quiet", bool, default=True, help_text="Suppress version/banner header"),
            ParamSpec("wide", bool, default=False, help_text="Wide output format"),
            ParamSpec("show_each", bool, default=False, help_text="Show all ciphers tested, not just accepted"),
            ParamSpec("mapping", str, default="", help_text="openssl, iana, rfc, no-openssl, no-iana, no-rfc"),
            ParamSpec("color", int, default=0, help_text="0, 1, 2, or 3"),
            ParamSpec("colorblind", bool, default=False, help_text="Use blue instead of green"),
            ParamSpec("debug", int, default=0, help_text="Debug level 0-6"),
            ParamSpec("disable_rating", bool, default=False, help_text="Disable rating"),
            ParamSpec("logfile", str, default="", help_text="Log file path"),
            ParamSpec("json_output", bool, default=False, help_text="Write JSON output"),
            ParamSpec("jsonfile", str, default="", help_text="JSON output file path"),
            ParamSpec("json_pretty", bool, default=False, help_text="Write pretty-printed JSON"),
            ParamSpec("jsonfile_pretty", str, default="", help_text="Pretty JSON output file path"),
            ParamSpec("csv_output", bool, default=False, help_text="Write CSV output"),
            ParamSpec("csvfile", str, default="", help_text="CSV output file path"),
            ParamSpec("html_output", bool, default=False, help_text="Write HTML output"),
            ParamSpec("htmlfile", str, default="", help_text="HTML output file path"),
            ParamSpec("outfile", str, default="", help_text="Generic output file path"),
            ParamSpec("hints", bool, default=False, help_text="Output additional hints"),
            ParamSpec("severity", str, default="", help_text="LOW, MEDIUM, HIGH, CRITICAL"),
            ParamSpec("append", bool, default=False, help_text="Append to existing output file"),
            ParamSpec("overwrite", bool, default=False, help_text="Overwrite existing output file"),
            ParamSpec("outprefix", str, default="", help_text="Prefix for output file names"),
            ParamSpec("additional_args", str, default="", help_text="Additional raw testssl.sh arguments"),
        ],
        build_command=_testssl_command,
        use_cache=False,
        use_recovery=True,
    ),
    ToolSpec(
        name="waymore",
        mcp_tool_name="waymore_discovery",
        endpoint="/api/tools/waymore",
        category="web_probe",
        description="Execute Waymore for URL and response discovery from multiple archive sources.",
        params=[
            ParamSpec("input", str, required=True, help_text="Target domain or URL to search"),
            ParamSpec("mode", str, default="U", help_text="Discovery mode — U (URLs only), R (responses only), or B (both)"),
            ParamSpec("output_urls", str, default="", help_text="File path to write discovered URLs to (optional)"),
            ParamSpec("output_responses", str, default="", help_text="Directory path to write responses to (optional)"),
            ParamSpec("limit", str, default="", help_text="Limit number of results"),
            ParamSpec("timeout", str, default="", help_text="Request timeout"),
            ParamSpec("verbose", bool, default=False, help_text="Verbose output"),
            ParamSpec("no_subs", bool, default=False, help_text="Exclude subdomains"),
        ],
        build_command=_waymore_command,
        use_recovery=True,
    ),
]

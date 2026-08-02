import shlex

from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError

_SCHEMATHESIS_MODES = {"positive", "negative", "all"}


def _api_fuzzer_command(p: dict):
    if p["endpoints"]:
        commands = []
        for endpoint in p["endpoints"]:
            for method in p["methods"]:
                test_url = f"{p['base_url'].rstrip('/')}/{str(endpoint).lstrip('/')}"
                argv = ["curl", "-s", "-X", method, "-w", "%{http_code}|%{size_download}", test_url]
                commands.append(shlex.join(argv))
        return commands
    argv = [
        "ffuf", "-u", f"{p['base_url']}/FUZZ", "-w", p["wordlist"],
        "-mc", "200,201,202,204,301,302,307,401,403,405", "-t", "50",
    ]
    return shlex.join(argv)


def _api_fuzzer_postprocess(raw, p: dict) -> dict:
    if isinstance(raw, list):
        results = []
        i = 0
        for endpoint in p["endpoints"]:
            for method in p["methods"]:
                results.append({"endpoint": endpoint, "method": method, "result": raw[i]})
                i += 1
        return {"success": True, "fuzzing_type": "endpoint_testing", "results": results}
    return {"success": True, "fuzzing_type": "endpoint_discovery", "result": raw}


def _schemathesis_command(p: dict) -> str:
    mode = str(p["mode"]).lower() if p["mode"] else ""
    if mode and mode not in _SCHEMATHESIS_MODES:
        raise ToolValidationError("mode must be one of 'positive', 'negative', 'all'")

    parts = ["schemathesis", "run", shlex.quote(str(p["schema"]))]
    if p["checks"]:
        parts += ["--checks", shlex.quote(str(p["checks"]))]
    if p["workers"]:
        parts += ["--workers", str(int(p["workers"]))]
    if p["max_examples"]:
        parts += ["--max-examples", str(int(p["max_examples"]))]
    if p["request_timeout"]:
        parts += ["--request-timeout", str(int(p["request_timeout"]))]
    if p["base_url"]:
        parts += ["--url", shlex.quote(str(p["base_url"]))]
    if p["auth"]:
        parts += ["--auth", shlex.quote(str(p["auth"]))]
    if p["headers"]:
        for hdr in [h.strip() for h in str(p["headers"]).split(";") if h.strip()]:
            parts += ["-H", shlex.quote(hdr)]
    if p["phases"]:
        parts += ["--phases", shlex.quote(str(p["phases"]))]
    if mode:
        parts += ["--mode", shlex.quote(mode)]
    if p["rate_limit"]:
        parts += ["--rate-limit", shlex.quote(str(p["rate_limit"]))]
    if p["report_formats"]:
        fmts = ",".join(f.strip() for f in str(p["report_formats"]).split(",") if f.strip())
        if fmts:
            parts += ["--report", shlex.quote(fmts)]
    if p["report_dir"]:
        parts += ["--report-dir", shlex.quote(str(p["report_dir"]))]
    if p["include_operation_id"]:
        for op in [o.strip() for o in str(p["include_operation_id"]).split(",") if o.strip()]:
            parts += ["--include-operation-id", shlex.quote(op)]
    if p["exclude_operation_id"]:
        for op in [o.strip() for o in str(p["exclude_operation_id"]).split(",") if o.strip()]:
            parts += ["--exclude-operation-id", shlex.quote(op)]
    if p["max_failures"] and int(p["max_failures"]) > 0:
        parts += ["--max-failures", str(int(p["max_failures"]))]
    if p["additional_args"]:
        parts.append(str(p["additional_args"]))
    return " ".join(parts)


def _schemathesis_postprocess(raw: dict, p: dict) -> dict:
    # Schemathesis exit codes: 0 = no findings, 1 = findings, 2 = usage/config error.
    # Treat "ran to completion" (0 or 1) as success=True and surface a separate
    # `findings` flag so callers can distinguish "clean run with issues" from
    # "tool failed to run".
    rc = raw.get("return_code")
    timed_out = bool(raw.get("timed_out"))
    if timed_out or rc is None:
        raw["success"] = False
        raw["findings"] = None
    elif rc in (0, 1):
        raw["success"] = True
        raw["findings"] = rc == 1
    else:
        raw["success"] = False
        raw["findings"] = None
    return raw


SPECS = [
    ToolSpec(
        name="api_fuzzer",
        mcp_tool_name="api_fuzzer",
        endpoint="/api/tools/api_fuzzer",
        category="api_fuzz",
        description="Advanced API endpoint fuzzing with intelligent parameter discovery.",
        params=[
            ParamSpec("base_url", str, required=True, help_text="Base URL of the API"),
            ParamSpec("endpoints", list, default=[], help_text="Specific endpoints to test"),
            ParamSpec("methods", list, default=["GET", "POST", "PUT", "DELETE"],
                      help_text="HTTP methods to test"),
            ParamSpec("wordlist", str, default="/usr/share/wordlists/api/api-endpoints.txt",
                      help_text="Wordlist for endpoint discovery"),
        ],
        build_command=_api_fuzzer_command,
        postprocess=_api_fuzzer_postprocess,
        use_recovery=True,
    ),
    ToolSpec(
        name="schemathesis",
        mcp_tool_name="schemathesis",
        endpoint="/api/tools/api_fuzz/schemathesis",
        category="api_fuzz",
        description="Run Schemathesis property-based API testing against an OpenAPI or GraphQL schema.",
        params=[
            ParamSpec("schema", str, required=True,
                      help_text="URL or file path to the OpenAPI/GraphQL schema"),
            ParamSpec("base_url", str, default="", help_text="Override the API base URL from the schema"),
            ParamSpec("checks", str, default="all", help_text="Comma-separated checks to run"),
            ParamSpec("workers", int, default=1, help_text="Number of parallel workers"),
            ParamSpec("max_examples", int, default=100, help_text="Hypothesis max examples per endpoint"),
            ParamSpec("headers", str, default="", help_text="Extra headers as 'Name: value' pairs separated by ';'"),
            ParamSpec("auth", str, default="", help_text="Basic auth credentials in 'user:pass' form"),
            ParamSpec("request_timeout", int, default=10, help_text="Per-request timeout in seconds"),
            ParamSpec("timeout", int, default=600, help_text="Overall run timeout in seconds"),
            ParamSpec("phases", str, default="", help_text="Comma-separated phases to run"),
            ParamSpec("mode", str, default="", help_text="Test data generation mode: positive, negative, or all"),
            ParamSpec("rate_limit", str, default="", help_text="Throttle requests, e.g. '3/s', '120/m'"),
            ParamSpec("report_formats", str, default="", help_text="Comma-separated report formats"),
            ParamSpec("report_dir", str, default="", help_text="Directory to write reports into"),
            ParamSpec("include_operation_id", str, default="", help_text="Comma-separated operationIds to include"),
            ParamSpec("exclude_operation_id", str, default="", help_text="Comma-separated operationIds to exclude"),
            ParamSpec("max_failures", int, default=0, help_text="Stop the run after N failures (0 disables)"),
            ParamSpec("additional_args", str, default="", help_text="Additional schemathesis flags to pass through"),
        ],
        build_command=_schemathesis_command,
        postprocess=_schemathesis_postprocess,
        timeout_param="timeout",
        use_recovery=True,
    ),
]

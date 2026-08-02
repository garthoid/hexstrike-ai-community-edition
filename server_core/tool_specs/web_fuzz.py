import shlex

from server_core.singletons import COMMON_DIRB_PATH, COMMON_DIRSEARCH_PATH
from server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError

DEFAULT_WFUZZ_WORDLIST = "/usr/share/wfuzz/wordlist/general/common.txt"


def _dirb_command(p: dict) -> str:
    argv = ["dirb", p["url"], p["wordlist"]]
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _dirsearch_command(p: dict) -> str:
    argv = ["dirsearch", "-u", p["url"], "-e", p["extensions"], "-w", p["wordlist"], "-t", str(p["threads"])]
    if p["recursive"]:
        argv.append("-r")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _dotdotpwn_command(p: dict) -> str:
    argv = ["dotdotpwn", "-m", p["module"], "-h", p["target"]]
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    argv.append("-b")
    return shlex.join(argv)


def _feroxbuster_command(p: dict) -> str:
    argv = ["feroxbuster", "-u", p["url"], "-w", p["wordlist"], "-t", str(p["threads"])]
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _ffuf_command(p: dict) -> str:
    url, wordlist, mode = p["url"], p["wordlist"], p["mode"]
    argv = ["ffuf"]
    if mode == "directory":
        argv.append("-u")
        argv.append(f"{url}/FUZZ")
        argv.append("-w")
        argv.append(wordlist)
    elif mode == "vhost":
        argv.append("-u")
        argv.append(url)
        argv.append("-H")
        argv.append("Host: FUZZ")
        argv.append("-w")
        argv.append(wordlist)
    elif mode == "parameter":
        argv.append("-u")
        argv.append(f"{url}?FUZZ=value")
        argv.append("-w")
        argv.append(wordlist)
    else:
        argv.append("-u")
        argv.append(url)
        argv.append("-w")
        argv.append(wordlist)
    argv.append("-mc")
    argv.append(p["match_codes"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _gobuster_command(p: dict) -> str:
    if p["mode"] not in ["dir", "dns", "fuzz", "vhost"]:
        raise ToolValidationError(f"Invalid mode: {p['mode']}. Must be one of: dir, dns, fuzz, vhost")
    argv = ["gobuster", p["mode"], "-u", p["url"], "-w", p["wordlist"]]
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _wfuzz_command(p: dict) -> str:
    target_url = p["url"]
    additional_args = p["additional_args"]
    if "FUZZ" not in target_url and "FUZ" not in target_url and " -V" not in f" {additional_args} ":
        target_url = f"{target_url.rstrip('/')}/FUZZ"

    default_args = "-c --hc 404"
    effective_args = f"{default_args} {additional_args}".strip()
    return f"wfuzz {effective_args} -z file,{shlex.quote(p['wordlist'])} {shlex.quote(target_url)}"


SPECS = [
    ToolSpec(
        name="dirb",
        mcp_tool_name="dirb_scan",
        endpoint="/api/tools/dirb",
        category="web_fuzz",
        description="Execute dirb for directory brute forcing.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("wordlist", str, default=COMMON_DIRB_PATH, help_text="Path to wordlist file"),
            ParamSpec("additional_args", str, default="", help_text="Additional Dirb arguments"),
        ],
        build_command=_dirb_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="dirsearch",
        mcp_tool_name="dirsearch_scan",
        endpoint="/api/tools/dirsearch",
        category="web_fuzz",
        description="Execute Dirsearch for advanced directory and file discovery.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("extensions", str, default="php,html,js,txt,xml,json", help_text="File extensions to search for"),
            ParamSpec("wordlist", str, default=COMMON_DIRSEARCH_PATH, help_text="Wordlist file to use"),
            ParamSpec("threads", int, default=30, help_text="Number of threads to use"),
            ParamSpec("recursive", bool, default=False, help_text="Enable recursive scanning"),
            ParamSpec("additional_args", str, default="", help_text="Additional Dirsearch arguments"),
        ],
        build_command=_dirsearch_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="dotdotpwn",
        mcp_tool_name="dotdotpwn_scan",
        endpoint="/api/tools/dotdotpwn",
        category="web_fuzz",
        description="Execute DotDotPwn for directory traversal testing.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target hostname or IP"),
            ParamSpec("module", str, default="http", help_text="Module to use (http, ftp, tftp, etc.)"),
            ParamSpec("additional_args", str, default="", help_text="Additional DotDotPwn arguments"),
        ],
        build_command=_dotdotpwn_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="feroxbuster",
        mcp_tool_name="feroxbuster_scan",
        endpoint="/api/tools/feroxbuster",
        category="web_fuzz",
        description="Execute Feroxbuster for recursive content discovery.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("wordlist", str, default=COMMON_DIRB_PATH, help_text="Wordlist file to use"),
            ParamSpec("threads", int, default=10, help_text="Number of threads"),
            ParamSpec("additional_args", str, default="", help_text="Additional Feroxbuster arguments"),
        ],
        build_command=_feroxbuster_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="ffuf",
        mcp_tool_name="ffuf_scan",
        endpoint="/api/tools/ffuf",
        category="web_fuzz",
        description="Execute FFuf for web fuzzing.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("wordlist", str, default=COMMON_DIRB_PATH, help_text="Wordlist file to use"),
            ParamSpec("mode", str, default="directory", help_text="Fuzzing mode (directory, vhost, parameter)"),
            ParamSpec("match_codes", str, default="200,204,301,302,307,401,403", help_text="HTTP status codes to match"),
            ParamSpec("additional_args", str, default="", help_text="Additional FFuf arguments"),
        ],
        build_command=_ffuf_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="gobuster",
        mcp_tool_name="gobuster_scan",
        endpoint="/api/tools/gobuster",
        category="web_fuzz",
        description="Execute Gobuster to find directories, DNS subdomains, or virtual hosts.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("mode", str, default="dir", help_text="Scan mode (dir, dns, fuzz, vhost)"),
            ParamSpec("wordlist", str, default=COMMON_DIRB_PATH, help_text="Path to wordlist file"),
            ParamSpec("additional_args", str, default="", help_text="Additional Gobuster arguments"),
        ],
        build_command=_gobuster_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="wfuzz",
        mcp_tool_name="wfuzz_scan",
        endpoint="/api/tools/wfuzz",
        category="web_fuzz",
        description="Execute Wfuzz for web application fuzzing.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL (use FUZZ where you want to inject payloads)"),
            ParamSpec("wordlist", str, default=DEFAULT_WFUZZ_WORDLIST, help_text="Wordlist file to use"),
            ParamSpec("additional_args", str, default="", help_text="Additional Wfuzz arguments"),
        ],
        build_command=_wfuzz_command,
        use_recovery=True,
    ),
]

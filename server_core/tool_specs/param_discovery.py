import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _arjun_command(p: dict) -> str:
    argv = ["arjun", "-u", p["url"], "-m", p["method"], "-t", str(p["threads"])]
    if p["wordlist"]:
        argv.append("-w")
        argv.append(p["wordlist"])
    if p["delay"] and int(p["delay"]) > 0:
        argv.append("-d")
        argv.append(str(p["delay"]))
    if p["stable"]:
        argv.append("--stable")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _paramspider_command(p: dict) -> str:
    argv = ["paramspider", "-d", p["domain"], "-l", str(p["level"])]
    if p["exclude"]:
        argv.append("--exclude")
        argv.append(p["exclude"])
    if p["output"]:
        argv.append("-o")
        argv.append(p["output"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _x8_command(p: dict) -> str:
    argv = ["x8", "-u", p["url"], "-w", p["wordlist"], "-X", p["method"]]
    if p["body"]:
        argv.append("-b")
        argv.append(p["body"])
    if p["headers"]:
        argv.append("-H")
        argv.append(p["headers"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="arjun",
        mcp_tool_name="arjun_parameter_discovery",
        endpoint="/api/tools/arjun",
        category="param_discovery",
        description="Execute Arjun for HTTP parameter discovery with enhanced logging.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("method", str, default="GET", help_text="HTTP method to use"),
            ParamSpec("wordlist", str, default="", help_text="Custom wordlist file"),
            ParamSpec("delay", int, default=0, help_text="Delay between requests"),
            ParamSpec("threads", int, default=25, help_text="Number of threads"),
            ParamSpec("stable", bool, default=False, help_text="Use stable mode"),
            ParamSpec("additional_args", str, default="", help_text="Additional Arjun arguments"),
        ],
        build_command=_arjun_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="paramspider",
        mcp_tool_name="paramspider_mining",
        endpoint="/api/tools/paramspider",
        category="param_discovery",
        description="Execute ParamSpider for parameter mining from web archives with enhanced logging.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain"),
            ParamSpec("level", int, default=2, help_text="Mining level depth"),
            ParamSpec("exclude", str, default="png,jpg,gif,jpeg,swf,woff,svg,pdf,css,ico",
                      help_text="File extensions to exclude"),
            ParamSpec("output", str, default="", help_text="Output file path"),
            ParamSpec("additional_args", str, default="", help_text="Additional ParamSpider arguments"),
        ],
        build_command=_paramspider_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="x8",
        mcp_tool_name="x8_parameter_discovery",
        endpoint="/api/tools/x8",
        category="param_discovery",
        description="Execute x8 for hidden parameter discovery with enhanced logging.",
        params=[
            ParamSpec("url", str, required=True, help_text="The target URL"),
            ParamSpec("wordlist", str, default="/usr/share/wordlists/x8/params.txt",
                      help_text="Parameter wordlist"),
            ParamSpec("method", str, default="GET", help_text="HTTP method"),
            ParamSpec("body", str, default="", help_text="Request body"),
            ParamSpec("headers", str, default="", help_text="Custom headers"),
            ParamSpec("additional_args", str, default="", help_text="Additional x8 arguments"),
        ],
        build_command=_x8_command,
        use_recovery=True,
    ),
]

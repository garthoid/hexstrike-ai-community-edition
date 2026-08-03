import shlex

from backend.server_core.tool_spec import ParamSpec, ToolSpec


def _gau_command(p: dict) -> str:
    argv = ["gau", p["domain"]]
    if p["providers"] != "wayback,commoncrawl,otx,urlscan":
        argv.append("--providers")
        argv.append(p["providers"])
    if p["include_subs"]:
        argv.append("--subs")
    if p["blacklist"]:
        argv.append("--blacklist")
        argv.append(p["blacklist"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _waybackurls_command(p: dict) -> str:
    argv = ["waybackurls", p["domain"]]
    if p["get_versions"]:
        argv.append("--get-versions")
    if p["no_subs"]:
        argv.append("--no-subs")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="gau",
        mcp_tool_name="gau_discovery",
        endpoint="/api/tools/gau",
        category="url_recon",
        description="Execute Gau (Get All URLs) for URL discovery from multiple sources.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain"),
            ParamSpec("providers", str, default="wayback,commoncrawl,otx,urlscan", help_text="Data providers to use"),
            ParamSpec("include_subs", bool, default=True, help_text="Include subdomains"),
            ParamSpec("blacklist", str, default="png,jpg,gif,jpeg,swf,woff,svg,pdf,css,ico", help_text="File extensions to blacklist"),
            ParamSpec("additional_args", str, default="", help_text="Additional Gau arguments"),
        ],
        build_command=_gau_command,
        use_recovery=True,
    ),
    ToolSpec(
        name="waybackurls",
        mcp_tool_name="waybackurls_discovery",
        endpoint="/api/tools/waybackurls",
        category="url_recon",
        description="Execute Waybackurls for historical URL discovery.",
        params=[
            ParamSpec("domain", str, required=True, help_text="The target domain"),
            ParamSpec("get_versions", bool, default=False, help_text="Get all versions of URLs"),
            ParamSpec("no_subs", bool, default=False, help_text="Don't include subdomains"),
            ParamSpec("additional_args", str, default="", help_text="Additional Waybackurls arguments"),
        ],
        build_command=_waybackurls_command,
        use_recovery=True,
    ),
]

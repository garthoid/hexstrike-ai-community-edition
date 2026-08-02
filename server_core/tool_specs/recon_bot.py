import shlex

from server_core.tool_spec import ParamSpec, ToolSpec


def _bbot_command(p: dict) -> str:
    argv = ["bbot", "-t", p["target"]]
    for key, value in p["parameters"].items():
        if isinstance(value, str) and value:
            argv.append(f"-{key}")
            argv.append(value)
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="bbot",
        mcp_tool_name="bbot_scan",
        endpoint="/api/bot/bbot",
        category="recon_bot",
        description="Run BBot for reconnaissance and enumeration tasks.",
        params=[
            ParamSpec("target", str, required=True, help_text="The domain or IP address to scan"),
            ParamSpec(
                "parameters",
                dict,
                required=True,
                help_text=(
                    "BBot flags and module options: f (enable flags, e.g. 'subdomain-enum'), "
                    "rf (require module flag, e.g. 'safe'), ef (exclude flags, e.g. 'slow'), "
                    "em (exclude modules, e.g. 'ipneighbor')"
                ),
            ),
        ],
        build_command=_bbot_command,
        use_cache=False,
        use_recovery=True,
    ),
]

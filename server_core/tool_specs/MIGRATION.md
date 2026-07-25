# Migrating a tool category to ToolSpec

This repeatable pattern replaces the hand-written per-tool boilerplate in
`server_api/<category>/` and `mcp_tools/<category>/` with a single declarative
`ToolSpec` per tool (see `server_core/tool_spec.py`). It was seeded by migrating
`net_lookup` (whois, dig, http-headers) and `dns_enum` (fierce, dnsenum) — see
those two modules as worked examples. Migrate one category per session/PR; don't
batch multiple categories in one pass.

## Steps

1. **Enumerate the category's files.**
   ```
   find server_api/<category> mcp_tools/<category> -name '*.py'
   ```
   Read every pair of files fully. Note any tool whose response isn't a plain
   `jsonify(execute_command(...))` passthrough (needs a `postprocess`), or that
   issues more than one shell command per request (needs `build_command` to
   return a `list[str]` instead of `str` — `ToolSpec.build_command` supports
   both, see `dig` in `server_core/tool_specs/net_lookup.py`).

2. **Write `server_core/tool_specs/<category>.py`** with one `ToolSpec` per
   tool. Hand-port each tool's `build_command` (and `postprocess`, if needed)
   verbatim from the old file's logic — this is the one part that stays
   genuinely hand-written, just isolated from all the Flask/FastMCP ceremony
   around it. Keep `category` as the directory name (not `tool_registry.py`'s
   taxonomy — those are deliberately different, see step 6).

3. **Delete the old per-tool files** on both sides.

4. **Update the category `__init__.py`s**:
   ```python
   # server_api/<category>/__init__.py
   from server_core.tool_specs.<category> import SPECS
   from server_api._generic.blueprint_factory import make_blueprint

   BLUEPRINTS = [make_blueprint(spec) for spec in SPECS]
   ```
   ```python
   # mcp_tools/<category>/__init__.py
   from server_core.tool_specs.<category> import SPECS
   from mcp_tools._generic.registrar import register_tool_from_spec

   def register_<category>_tools(mcp, api_client, logger):
       for spec in SPECS:
           register_tool_from_spec(mcp, api_client, logger, spec)
   ```

5. **Wire the category into the two registration points, for this category
   only:**
   - `server_api/__init__.py`: change `from .<category> import *` to
     `from . import <category>`, and replace that category's explicit
     `app.register_blueprint(api_..._bp)` lines in `register_blueprints()`
     with `for bp in <category>.BLUEPRINTS: app.register_blueprint(bp)`.
   - `mcp_core/tool_profiles.py`: replace that category's list of per-tool
     lambdas with a single
     `lambda mcp, client, logger: register_<category>_tools(mcp, client, logger)`.

6. **Cross-check `tool_registry.py`.** For each migrated tool, verify its
   `TOOLS[name]["params"]`/`["optional"]` match the new `ToolSpec`'s params
   (use `server_core.tool_spec.to_tool_definition(spec)` as a diffing aid).
   Fix drift if found (this migration fixed two: `fierce`/`dnsenum` were each
   missing `dns_server` from `optional`). **Never** change `category` or
   `effectiveness` — those are a separate, hand-curated taxonomy for the
   decision engine, intentionally different from the directory-based
   `category` on `ToolSpec`.

7. **Extend `tests/test_endpoints_exist.py`** with a `test_<tool>` per newly
   migrated tool in the category's test class (route-existence check only,
   `execute_command` is mocked globally by that file). Create the test class if
   the category has none yet (e.g. `osint`, `credential_harvest` had zero
   coverage before migration).

8. **Check `tests/test_tool_command_builders.py` for stale patch targets.**
   `grep -n '"server_api\.<category>\.' tests/test_tool_command_builders.py` —
   this file has richer per-tool command-assertion tests with a hardcoded
   `_<TOOL>_PATCH = "server_api.<category>.<tool>.execute_command"` string used
   with `unittest.mock.patch(...)`. Deleting the old per-tool file breaks that
   patch target (`AttributeError: module has no attribute '<tool>'`) since
   `execute_command` is no longer imported into a per-tool module — it now
   lives only in `server_api/_generic/blueprint_factory.py`. Fix by updating
   the constant to `"server_api._generic.blueprint_factory.execute_command"`
   (found and fixed for `nuclei` in the `vuln_scan` migration — this is easy
   to miss since `test_endpoints_exist.py` alone won't catch it, only a full
   suite run will).

9. **Verify**:
   - `./nyxstrike-env/bin/pytest tests/test_endpoints_exist.py -k "<tool names>"`
   - Manual Flask smoke test: start the server, POST sample payloads to each
     migrated endpoint, diff response shape against a pre-migration capture.
   - MCP discoverability: `setup_mcp_server(api_client, logger, profiles=[<category>])`,
     then `await mcp.list_tools()` — confirm each tool's name/description/`parameters`
     schema match the old hand-written wrapper's signature+docstring.
   - `git diff --stat` should touch only this category's files plus the two
     registration-wiring files — nothing in `server_core/_generic`,
     `server_api/_generic`, or `mcp_tools/_generic` (those are shared, already built).
   - Run the **full** test suite at least once before considering the category
     done — `test_tool_command_builders.py`'s stale-patch failures (step 8)
     only surface there, not in a `-k`-filtered targeted run.

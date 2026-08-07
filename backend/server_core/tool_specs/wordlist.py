from backend.server_core.singletons import wordlist_store
from backend.server_core.tool_spec import ParamSpec, ToolNotFoundError, ToolSpec


def _wordlist_get_handler(p: dict) -> dict:
    wordlist = wordlist_store.load(p["wordlist_id"])
    if wordlist is None:
        raise ToolNotFoundError("Wordlist not found")
    return wordlist


def _wordlist_get_all_handler(p: dict) -> dict:
    return wordlist_store.load_all()


def _wordlist_get_path_handler(p: dict) -> dict:
    path = wordlist_store.getPath(p["wordlist_id"])
    if path is None:
        raise ToolNotFoundError("Wordlist not found or missing path")
    return path


def _wordlist_find_best_handler(p: dict) -> dict:
    best_match = wordlist_store.find_best_match(p["criteria"])
    if best_match is None:
        raise ToolNotFoundError("No matching wordlist found")
    return best_match


def _wordlist_save_handler(p: dict) -> dict:
    success = wordlist_store.save(p["wordlist_id"], p["wordlist_info"])
    if not success:
        raise RuntimeError("Failed to save wordlist")
    return {"status": "success"}


def _wordlist_delete_handler(p: dict) -> dict:
    success = wordlist_store.delete(p["wordlist_id"])
    if not success:
        raise RuntimeError("Failed to delete wordlist")
    return {"status": "success"}


SPECS = [
    ToolSpec(
        name="wordlist_get",
        mcp_tool_name="wordlist_get",
        endpoint="/api/wordlists/<wordlist_id>",
        category="wordlist",
        description="Retrieve a specific wordlist entry by its ID.",
        method="GET",
        params=[
            ParamSpec("wordlist_id", str, required=True, help_text="The unique identifier of the wordlist"),
        ],
        handler=_wordlist_get_handler,
    ),
    ToolSpec(
        name="wordlist_get_all",
        mcp_tool_name="wordlist_get_all",
        endpoint="/api/wordlists",
        category="wordlist",
        description="Retrieve all wordlist entries.",
        method="GET",
        handler=_wordlist_get_all_handler,
    ),
    ToolSpec(
        name="wordlist_get_path",
        mcp_tool_name="wordlist_get_path",
        endpoint="/api/wordlists/<wordlist_id>/path",
        category="wordlist",
        description="Retrieve the file path for a specific wordlist by its ID.",
        method="GET",
        params=[
            ParamSpec("wordlist_id", str, required=True, help_text="The unique identifier of the wordlist"),
        ],
        handler=_wordlist_get_path_handler,
    ),
    ToolSpec(
        name="wordlist_find_best",
        mcp_tool_name="wordlist_find_best",
        endpoint="/api/wordlists/bestmatch",
        category="wordlist",
        description="Find the best matching wordlist based on provided criteria.",
        params=[
            ParamSpec(
                "criteria", dict, required=True,
                help_text=(
                    "Search criteria for the wordlist, e.g. "
                    '{"type": "password", "recommended_for": ["brute-force"], "speed": "fast"}'
                ),
            ),
        ],
        handler=_wordlist_find_best_handler,
    ),
    ToolSpec(
        name="wordlist_save",
        mcp_tool_name="wordlist_save",
        endpoint="/api/wordlists/<wordlist_id>",
        category="wordlist",
        description="Save or update a wordlist entry in the wordlists.json file.",
        params=[
            ParamSpec("wordlist_id", str, required=True, help_text="Unique identifier for the wordlist"),
            ParamSpec(
                "wordlist_info", dict, required=True,
                help_text=(
                    "Metadata about the wordlist. Required fields: path (str), type (str). "
                    "Optional: description, recommended_for (list), size (int), tool (list), "
                    "speed, language, coverage, format."
                ),
            ),
        ],
        handler=_wordlist_save_handler,
    ),
    ToolSpec(
        name="wordlist_delete",
        mcp_tool_name="wordlist_delete",
        endpoint="/api/wordlists/<wordlist_id>",
        category="wordlist",
        description="Delete a specific wordlist entry by its ID.",
        method="DELETE",
        params=[
            ParamSpec("wordlist_id", str, required=True, help_text="The unique identifier of the wordlist"),
        ],
        handler=_wordlist_delete_handler,
    ),
]

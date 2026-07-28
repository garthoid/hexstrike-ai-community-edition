import sqlite3

import pymysql

from server_core.tool_spec import ParamSpec, ToolSpec


def _no_commands(p: dict) -> list:
    return []


def _mysql_postprocess(raw, params: dict) -> dict:
    try:
        conn = pymysql.connect(
            host=params["host"],
            user=params["user"],
            password=params["password"],
            database=params["database"],
            cursorclass=pymysql.cursors.DictCursor,
        )
        with conn.cursor() as cursor:
            cursor.execute(params["query"])
            result = cursor.fetchall()
        conn.close()
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _sqlite_postprocess(raw, params: dict) -> dict:
    try:
        conn = sqlite3.connect(params["db_path"])
        cur = conn.cursor()
        cur.execute(params["query"])
        result = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        conn.close()
        return {"success": True, "columns": columns, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


SPECS = [
    ToolSpec(
        name="mysql",
        mcp_tool_name="mysql_query",
        endpoint="/api/tools/mysql",
        category="db_query",
        description="Query a MySQL database.",
        params=[
            ParamSpec("host", str, required=True, help_text="MySQL server address"),
            ParamSpec("user", str, required=True, help_text="Username"),
            ParamSpec("password", str, default="", help_text="Password (optional)"),
            ParamSpec("database", str, default="", help_text="Database name"),
            ParamSpec("query", str, default="", help_text="SQL query"),
        ],
        build_command=_no_commands,
        postprocess=_mysql_postprocess,
    ),
    ToolSpec(
        name="sqlite",
        mcp_tool_name="sqlite_query",
        endpoint="/api/tools/sqlite",
        category="db_query",
        description="Query a SQLite database file.",
        params=[
            ParamSpec("db_path", str, required=True, help_text="Path to the SQLite database file"),
            ParamSpec("query", str, required=True, help_text="SQL query to execute"),
        ],
        build_command=_no_commands,
        postprocess=_sqlite_postprocess,
    ),
]

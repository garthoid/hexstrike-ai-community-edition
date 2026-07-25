"""Auto-discovery for ToolSpec-driven Flask blueprints.

Every migrated category lives entirely as one server_core/tool_specs/<category>.py
module — there is no per-category server_api/<category>/ package anymore. This
scans that package for SPECS lists and registers a blueprint per tool.
"""

import importlib
import pkgutil

import server_core.tool_specs as _tool_specs_pkg
from server_api._generic.blueprint_factory import make_blueprint


def register_all_toolspec_blueprints(app):
    for _, module_name, _ in pkgutil.iter_modules(_tool_specs_pkg.__path__):
        module = importlib.import_module(f"server_core.tool_specs.{module_name}")
        specs = getattr(module, "SPECS", None)
        if not specs:
            continue
        for spec in specs:
            app.register_blueprint(make_blueprint(spec))

"""Auto-discovery for ToolSpec-driven Flask blueprints.

Every migrated category lives entirely as one server_core/tool_specs/<category>.py
module — there is no per-category server_api/<category>/ package anymore. This
registers a blueprint per tool for every ToolSpec discovered by iter_all_specs().
"""

from server_api._generic.blueprint_factory import make_blueprint
from server_core.tool_spec import iter_all_specs


def register_all_toolspec_blueprints(app):
    for spec in iter_all_specs():
        app.register_blueprint(make_blueprint(spec))

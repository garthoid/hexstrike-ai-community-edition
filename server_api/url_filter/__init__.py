from server_core.tool_specs.url_filter import SPECS
from server_api._generic.blueprint_factory import make_blueprint

BLUEPRINTS = [make_blueprint(spec) for spec in SPECS]

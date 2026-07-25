from server_core.tool_specs.osint import SPECS
from server_api._generic.blueprint_factory import make_blueprint

BLUEPRINTS = [make_blueprint(spec) for spec in SPECS]

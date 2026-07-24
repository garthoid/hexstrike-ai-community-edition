"""Declarative tool description shared by server_api (Flask) and mcp_tools (FastMCP).

A single ToolSpec drives both the Flask blueprint (server_api/_generic/blueprint_factory.py)
and the FastMCP tool registration (mcp_tools/_generic/registrar.py), eliminating the
hand-written boilerplate each side used to duplicate per tool. This module must stay free
of Flask/FastMCP imports so neither runtime pulls in the other's dependencies.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union


@dataclass(frozen=True)
class ParamSpec:
    name: str
    type: type = str
    required: bool = False
    default: Any = ""
    help_text: str = ""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    mcp_tool_name: str
    endpoint: str
    category: str
    description: str
    params: List[ParamSpec] = field(default_factory=list)
    build_command: Optional[Callable[[Dict[str, Any]], Union[str, List[str]]]] = None
    postprocess: Optional[Callable[[Any, Dict[str, Any]], dict]] = None
    use_cache: bool = True
    timeout: Optional[int] = None
    timeout_param: Optional[str] = None
    use_recovery: bool = False


class ToolValidationError(Exception):
    """Raised by a build_command to signal a 400 response richer than the plain
    "<param> parameter is required" check the blueprint factory does automatically
    (e.g. an invalid enum value, or a required external binary that isn't installed).
    """

    def __init__(self, error: str, **extra: Any):
        super().__init__(error)
        self.error = error
        self.extra = extra


def to_tool_definition(spec: ToolSpec) -> dict:
    """Emit a tool_registry.py-compatible ToolDefinition dict from a ToolSpec.

    Does NOT set 'category' (tool_registry's curated taxonomy) or 'effectiveness'
    (hand-judged) — those are a separate concern from the mechanical param contract.
    Intended as a manual consistency check during migration, not an automatic sync.
    """
    return {
        "endpoint": spec.endpoint,
        "method": "POST",
        "desc": spec.description.strip().splitlines()[0] if spec.description else "",
        "params": {p.name: {"required": True} for p in spec.params if p.required},
        "optional": {p.name: p.default for p in spec.params if not p.required},
    }

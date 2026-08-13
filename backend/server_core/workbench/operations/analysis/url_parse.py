from urllib.parse import parse_qs, urlsplit

from backend.server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    if not text:
        raise ValueError("Input must not be empty")

    parsed = urlsplit(text)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError("Input must be a fully-qualified URL, e.g. https://example.com/path?a=1")

    lines = [f"Scheme: {parsed.scheme}", f"Host: {parsed.hostname or ''}"]
    if parsed.port:
        lines.append(f"Port: {parsed.port}")
    if parsed.username:
        lines.append(f"Username: {parsed.username}")
    if parsed.password:
        lines.append(f"Password: {parsed.password}")
    lines.append(f"Path: {parsed.path or '/'}")
    if parsed.query:
        lines.append("Query params:")
        for key, values in parse_qs(parsed.query, keep_blank_values=True).items():
            for value in values:
                lines.append(f"  {key} = {value}")
    if parsed.fragment:
        lines.append(f"Fragment: {parsed.fragment}")

    return {"output": "\n".join(lines)}


OPERATION = Operation(
    id="url_parse",
    category="analysis",
    name="URL Parser",
    description="Break a URL down into scheme, host, port, path, query params, and fragment.",
    run=run,
    params=[
        ParamSpec(name="input", label="URL", type="textarea", required=True),
    ],
)

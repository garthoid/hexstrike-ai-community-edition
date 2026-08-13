import secrets
import string

from backend.server_core.workbench.registry import Operation, ParamSpec

CHARSETS = {
    "alphanumeric": string.ascii_letters + string.digits,
    "letters": string.ascii_letters,
    "digits": string.digits,
    "hex": string.hexdigits.lower()[:16],
    "punctuation": string.ascii_letters + string.digits + string.punctuation,
}


def run(params: dict) -> dict:
    try:
        length = int(params.get("length", 16))
    except (TypeError, ValueError):
        raise ValueError("Length must be an integer")
    if length < 1 or length > 4096:
        raise ValueError("Length must be between 1 and 4096")
    charset_name = params.get("charset", "alphanumeric")
    if charset_name not in CHARSETS:
        raise ValueError(f"Unsupported charset: {charset_name}")
    alphabet = CHARSETS[charset_name]
    output = "".join(secrets.choice(alphabet) for _ in range(length))
    return {"output": output}


OPERATION = Operation(
    id="random_string_generate",
    category="text",
    name="Random String Generator",
    description="Generate a cryptographically random string.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="text", hidden=True),
        ParamSpec(name="length", label="Length", type="number", default=16),
        ParamSpec(
            name="charset",
            label="Charset",
            type="select",
            choices=list(CHARSETS.keys()),
            default="alphanumeric",
        ),
    ],
)

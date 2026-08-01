from server_core.workbench.registry import Operation, ParamSpec

MODES = ["to_charcode", "from_charcode"]
BASES = ["decimal", "hexadecimal"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    mode = params.get("mode", "to_charcode")
    base = params.get("base", "decimal")
    delimiter = params.get("delimiter", " ")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    if base not in BASES:
        raise ValueError(f"Unsupported base: {base}")

    if mode == "to_charcode":
        if base == "decimal":
            codes = [str(ord(c)) for c in text]
        else:
            codes = [format(ord(c), "x") for c in text]
        return {"output": delimiter.join(codes)}

    if not text.strip():
        raise ValueError("Input must not be empty")
    tokens = [t for t in (text.split(delimiter) if delimiter else text.split())]
    tokens = [t.strip() for t in tokens if t.strip()]
    try:
        chars = [chr(int(t, 16 if base == "hexadecimal" else 10)) for t in tokens]
    except ValueError:
        raise ValueError(f"Invalid {base} code point in input")
    return {"output": "".join(chars)}


OPERATION = Operation(
    id="charcode_convert",
    category="encoding",
    name="Charcode Convert",
    description="Convert text to a list of Unicode code points, or back from code points to text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="to_charcode"),
        ParamSpec(name="base", label="Base", type="select", choices=BASES, default="decimal"),
        ParamSpec(name="delimiter", label="Delimiter", type="text", default=" "),
    ],
)

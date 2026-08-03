from backend.server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    try:
        shift = int(params.get("shift", 3))
    except (TypeError, ValueError):
        raise ValueError("Shift must be an integer")

    out_chars = []
    for ch in text:
        if "a" <= ch <= "z":
            out_chars.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
        elif "A" <= ch <= "Z":
            out_chars.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
        else:
            out_chars.append(ch)
    return {"output": "".join(out_chars)}


OPERATION = Operation(
    id="caesar_cipher",
    category="ciphers",
    name="Caesar Cipher",
    description="Shift alphabetic characters by a fixed amount. Use a negative shift to decode.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="shift", label="Shift", type="number", default=3),
    ],
)

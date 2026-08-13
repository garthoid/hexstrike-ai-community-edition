import re

from backend.server_core.workbench.registry import Operation, ParamSpec

OCTAL_RE = re.compile(r"[0-7]{3,4}")
SYMBOLIC_RE = re.compile(r"[r-][w-][xsS-][r-][w-][xsS-][r-][w-][xtT-]")


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    if not text:
        raise ValueError("Input must not be empty")

    if OCTAL_RE.fullmatch(text):
        return {"output": _octal_to_symbolic(text)}

    body = text[1:] if len(text) == 10 else text
    if SYMBOLIC_RE.fullmatch(body):
        return {"output": _symbolic_to_octal(body)}

    raise ValueError("Input must be octal (e.g. 755) or symbolic (e.g. rwxr-xr-x) permissions")


def _octal_to_symbolic(text: str) -> str:
    digits = text[-3:]
    special = int(text[:-3]) if len(text) == 4 else 0
    letters = "rwx"
    perms = []
    for digit in digits:
        value = int(digit)
        for i, letter in enumerate(letters):
            perms.append(letter if value & (4 >> i) else "-")
    if special & 4:
        perms[2] = "s" if perms[2] == "x" else "S"
    if special & 2:
        perms[5] = "s" if perms[5] == "x" else "S"
    if special & 1:
        perms[8] = "t" if perms[8] == "x" else "T"
    return "".join(perms)


def _symbolic_to_octal(body: str) -> str:
    groups = [body[0:3], body[3:6], body[6:9]]
    digits = []
    special = 0
    for i, group in enumerate(groups):
        value = 0
        if group[0] == "r":
            value += 4
        if group[1] == "w":
            value += 2
        exec_char = group[2]
        if exec_char in ("x", "s", "t"):
            value += 1
        if exec_char in ("s", "S") and i == 0:
            special += 4
        if exec_char in ("s", "S") and i == 1:
            special += 2
        if exec_char in ("t", "T") and i == 2:
            special += 1
        digits.append(str(value))
    octal = "".join(digits)
    return f"{special}{octal}" if special else octal


OPERATION = Operation(
    id="unix_permissions",
    category="networking",
    name="Unix Permissions",
    description="Convert Unix file permissions between octal (755) and symbolic (rwxr-xr-x) form.",
    run=run,
    params=[
        ParamSpec(name="input", label="Permissions", type="text", required=True, help_text="e.g. 755 or rwxr-xr-x"),
    ],
)

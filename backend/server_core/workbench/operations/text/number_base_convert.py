from backend.server_core.workbench.registry import Operation, ParamSpec

BASES = {"binary": 2, "octal": 8, "decimal": 10, "hexadecimal": 16}
PREFIXES = {2: "0b", 8: "0o", 16: "0x"}


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    from_base = params.get("from_base", "decimal")
    to_base = params.get("to_base", "hexadecimal")
    if from_base not in BASES:
        raise ValueError(f"Unsupported source base: {from_base}")
    if to_base not in BASES:
        raise ValueError(f"Unsupported target base: {to_base}")
    try:
        value = int(text, BASES[from_base])
    except ValueError:
        raise ValueError(f"'{text}' is not a valid {from_base} number")

    target = BASES[to_base]
    if target == 10:
        output = str(value)
    elif target == 2:
        output = f"{PREFIXES[2]}{value:b}"
    elif target == 8:
        output = f"{PREFIXES[8]}{value:o}"
    else:
        output = f"{PREFIXES[16]}{value:x}"
    return {"output": output}


OPERATION = Operation(
    id="number_base_convert",
    category="text",
    name="Number Base Converter",
    description="Convert a number between binary, octal, decimal, and hexadecimal.",
    run=run,
    params=[
        ParamSpec(name="input", label="Number", type="text", required=True),
        ParamSpec(
            name="from_base",
            label="From",
            type="select",
            choices=list(BASES.keys()),
            default="decimal",
        ),
        ParamSpec(
            name="to_base",
            label="To",
            type="select",
            choices=list(BASES.keys()),
            default="hexadecimal",
        ),
    ],
)

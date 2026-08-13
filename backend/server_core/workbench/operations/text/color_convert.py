import re

from backend.server_core.workbench.registry import Operation, ParamSpec

FORMATS = ["hex", "rgb", "hsl"]

_HEX_RE = re.compile(r"^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$")
_RGB_RE = re.compile(r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", re.IGNORECASE)
_HSL_RE = re.compile(r"^hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$", re.IGNORECASE)


def _parse_hex(text: str) -> tuple:
    m = _HEX_RE.match(text.strip())
    if not m:
        raise ValueError("Invalid hex color, expected e.g. #ff0000 or #f00")
    hex_digits = m.group(1)
    if len(hex_digits) == 3:
        hex_digits = "".join(c * 2 for c in hex_digits)
    return tuple(int(hex_digits[i : i + 2], 16) for i in (0, 2, 4))


def _parse_rgb(text: str) -> tuple:
    m = _RGB_RE.match(text.strip())
    if not m:
        raise ValueError("Invalid rgb color, expected e.g. rgb(255, 0, 0)")
    r, g, b = (int(v) for v in m.groups())
    for channel in (r, g, b):
        if not 0 <= channel <= 255:
            raise ValueError(f"RGB channel out of range: {channel}")
    return r, g, b


def _rgb_to_hsl(r: int, g: int, b: int) -> tuple:
    rf, gf, bf = r / 255, g / 255, b / 255
    hi, lo = max(rf, gf, bf), min(rf, gf, bf)
    light = (hi + lo) / 2
    if hi == lo:
        hue = sat = 0.0
    else:
        delta = hi - lo
        sat = delta / (2 - hi - lo) if light > 0.5 else delta / (hi + lo)
        if hi == rf:
            hue = (gf - bf) / delta + (6 if gf < bf else 0)
        elif hi == gf:
            hue = (bf - rf) / delta + 2
        else:
            hue = (rf - gf) / delta + 4
        hue *= 60
    return round(hue), round(sat * 100), round(light * 100)


def _hsl_to_rgb(h: int, s: int, l: int) -> tuple:
    sf, lf = s / 100, l / 100
    c = (1 - abs(2 * lf - 1)) * sf
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = lf - c / 2
    if h < 60:
        rp, gp, bp = c, x, 0.0
    elif h < 120:
        rp, gp, bp = x, c, 0.0
    elif h < 180:
        rp, gp, bp = 0.0, c, x
    elif h < 240:
        rp, gp, bp = 0.0, x, c
    elif h < 300:
        rp, gp, bp = x, 0.0, c
    else:
        rp, gp, bp = c, 0.0, x
    return round((rp + m) * 255), round((gp + m) * 255), round((bp + m) * 255)


def _parse_hsl(text: str) -> tuple:
    m = _HSL_RE.match(text.strip())
    if not m:
        raise ValueError("Invalid hsl color, expected e.g. hsl(0, 100%, 50%)")
    h, s, l = (int(v) for v in m.groups())
    if not 0 <= h <= 360:
        raise ValueError(f"Hue out of range: {h}")
    for channel in (s, l):
        if not 0 <= channel <= 100:
            raise ValueError(f"Saturation/lightness out of range: {channel}")
    return h, s, l


def run(params: dict) -> dict:
    text = params.get("input", "")
    from_format = params.get("from_format", "hex")
    to_format = params.get("to_format", "rgb")
    if from_format not in FORMATS:
        raise ValueError(f"Unsupported from_format: {from_format}")
    if to_format not in FORMATS:
        raise ValueError(f"Unsupported to_format: {to_format}")

    if from_format == "hex":
        r, g, b = _parse_hex(text)
    elif from_format == "rgb":
        r, g, b = _parse_rgb(text)
    else:
        r, g, b = _hsl_to_rgb(*_parse_hsl(text))

    if to_format == "hex":
        output = "#{:02x}{:02x}{:02x}".format(r, g, b)
    elif to_format == "rgb":
        output = f"rgb({r}, {g}, {b})"
    else:
        h, s, l = _rgb_to_hsl(r, g, b)
        output = f"hsl({h}, {s}%, {l}%)"

    return {"output": output}


OPERATION = Operation(
    id="color_convert",
    category="text",
    name="Color Converter",
    description="Convert a color between hex, rgb(), and hsl() formats.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="text", required=True, help_text="e.g. #ff0000, rgb(255, 0, 0), or hsl(0, 100%, 50%)"),
        ParamSpec(name="from_format", label="From Format", type="select", choices=FORMATS, default="hex"),
        ParamSpec(name="to_format", label="To Format", type="select", choices=FORMATS, default="rgb"),
    ],
)

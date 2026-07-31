from datetime import datetime, timezone

from server_core.workbench.registry import Operation, ParamSpec

MODES = ["epoch_to_iso", "iso_to_epoch"]


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    mode = params.get("mode", "epoch_to_iso")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")
    if not text:
        raise ValueError("Input must not be empty")

    if mode == "epoch_to_iso":
        try:
            seconds = float(text)
        except ValueError:
            raise ValueError("Input must be a numeric Unix timestamp (seconds)")
        try:
            dt = datetime.fromtimestamp(seconds, tz=timezone.utc)
        except (OverflowError, OSError, ValueError) as e:
            raise ValueError(f"Timestamp out of range: {e}")
        return {"output": dt.isoformat().replace("+00:00", "Z")}

    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as e:
        raise ValueError(f"Invalid ISO 8601 timestamp: {e}")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return {"output": str(dt.timestamp())}


OPERATION = Operation(
    id="timestamp_convert",
    category="analysis",
    name="Timestamp Converter",
    description="Convert between Unix epoch seconds and ISO 8601 timestamps.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="text", required=True),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="epoch_to_iso"),
    ],
)

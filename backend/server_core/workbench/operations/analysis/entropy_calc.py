import math
from collections import Counter

from backend.server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    data = text.encode("utf-8", errors="surrogateescape")
    if not data:
        return {"output": "0.0"}
    counts = Counter(data)
    length = len(data)
    entropy = max(0.0, -sum((c / length) * math.log2(c / length) for c in counts.values()))
    return {"output": f"{entropy:.4f} bits/byte (max 8.0)"}


OPERATION = Operation(
    id="entropy_calc",
    category="analysis",
    name="Shannon Entropy",
    description="Calculate the Shannon entropy of the input, a rough measure of randomness.",
    run=run,
    params=[ParamSpec(name="input", label="Input", type="textarea", required=True)],
)

import binascii

from backend.server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "")
    key = params.get("key", "")
    if not key:
        raise ValueError("Key must not be empty")
    data = text.encode("utf-8", errors="surrogateescape")
    key_bytes = key.encode("utf-8", errors="surrogateescape")
    out = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
    return {"output": binascii.hexlify(out).decode("ascii")}


OPERATION = Operation(
    id="xor_cipher",
    category="ciphers",
    name="XOR Cipher",
    description="XOR text against a repeating key, output as hex.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="key", label="Key", type="text", required=True),
    ],
)

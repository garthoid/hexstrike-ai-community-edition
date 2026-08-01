import zlib

from server_core.workbench.registry import Operation, ParamSpec

ALGORITHMS = ["crc32", "adler32"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    algorithm = params.get("algorithm", "crc32")
    if algorithm not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    data = text.encode("utf-8", errors="surrogateescape")
    value = zlib.crc32(data) if algorithm == "crc32" else zlib.adler32(data)
    return {"output": f"{value:08x}"}


OPERATION = Operation(
    id="checksum",
    category="hashing",
    name="Checksum",
    description="Compute a CRC32 or Adler-32 checksum of text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="algorithm", label="Algorithm", type="select", choices=ALGORITHMS, default="crc32"),
    ],
)

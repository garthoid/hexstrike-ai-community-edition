import hashlib

from backend.server_core.workbench.registry import Operation, ParamSpec

ALGORITHMS = ["md5", "sha1", "sha256", "sha512", "sha3_256"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    algo = params.get("algorithm", "sha256")
    if algo not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algo}")
    digest = hashlib.new(algo, text.encode("utf-8", errors="surrogateescape")).hexdigest()
    return {"output": digest}


OPERATION = Operation(
    id="hash_digest",
    category="hashing",
    name="Hash Digest",
    description="Compute a cryptographic hash digest of text.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(
            name="algorithm",
            label="Algorithm",
            type="select",
            choices=ALGORITHMS,
            default="sha256",
        ),
    ],
)

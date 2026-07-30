import hashlib
import hmac

from server_core.workbench.registry import Operation, ParamSpec

ALGORITHMS = ["md5", "sha1", "sha256", "sha512"]


def run(params: dict) -> dict:
    message = params.get("input", "")
    key = params.get("key", "")
    algo = params.get("algorithm", "sha256")
    if algo not in ALGORITHMS:
        raise ValueError(f"Unsupported algorithm: {algo}")
    digest = hmac.new(
        key.encode("utf-8", errors="surrogateescape"),
        message.encode("utf-8", errors="surrogateescape"),
        getattr(hashlib, algo),
    ).hexdigest()
    return {"output": digest}


OPERATION = Operation(
    id="hmac_digest",
    category="hashing",
    name="HMAC Digest",
    description="Compute an HMAC of text using a secret key.",
    run=run,
    params=[
        ParamSpec(name="input", label="Message", type="textarea", required=True),
        ParamSpec(name="key", label="Key", type="text", required=True),
        ParamSpec(
            name="algorithm",
            label="Algorithm",
            type="select",
            choices=ALGORITHMS,
            default="sha256",
        ),
    ],
)

import json

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from backend.server_core.workbench.registry import Operation, ParamSpec


def _public_key_info(cert: "x509.Certificate") -> str:
    key = cert.public_key()
    if isinstance(key, rsa.RSAPublicKey):
        return f"RSA-{key.key_size}"
    if isinstance(key, ec.EllipticCurvePublicKey):
        return f"EC-{key.curve.name}"
    return type(key).__name__


def run(params: dict) -> dict:
    text = params.get("input", "")
    try:
        cert = x509.load_pem_x509_certificate(text.encode("utf-8"))
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid PEM certificate: {e}")

    try:
        sans = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        sans = []

    info = {
        "subject": cert.subject.rfc4514_string(),
        "issuer": cert.issuer.rfc4514_string(),
        "serial_number": format(cert.serial_number, "x"),
        "not_valid_before": cert.not_valid_before_utc.isoformat(),
        "not_valid_after": cert.not_valid_after_utc.isoformat(),
        "signature_algorithm": cert.signature_algorithm_oid._name,
        "public_key": _public_key_info(cert),
        "subject_alternative_names": sans,
    }
    return {"output": json.dumps(info, indent=2)}


OPERATION = Operation(
    id="x509_parse",
    category="analysis",
    name="X.509 Certificate Parser",
    description="Parse a PEM certificate and show its subject, issuer, validity window, and other details.",
    run=run,
    params=[ParamSpec(name="input", label="PEM Certificate", type="textarea", required=True)],
)

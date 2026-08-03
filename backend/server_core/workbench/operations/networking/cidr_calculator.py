import ipaddress

from backend.server_core.workbench.registry import Operation, ParamSpec


def run(params: dict) -> dict:
    text = params.get("input", "").strip()
    if not text:
        raise ValueError("Input must not be empty")
    try:
        network = ipaddress.ip_network(text, strict=False)
    except ValueError as e:
        raise ValueError(f"Invalid CIDR: {e}")

    hosts = list(network.hosts())
    lines = [
        f"Network: {network.network_address}",
        f"Broadcast: {network.broadcast_address}",
        f"Netmask: {network.netmask}",
        f"Prefix length: /{network.prefixlen}",
        f"Total addresses: {network.num_addresses}",
        f"Usable hosts: {len(hosts)}",
    ]
    if hosts:
        lines.append(f"Usable range: {hosts[0]} - {hosts[-1]}")
    return {"output": "\n".join(lines)}


OPERATION = Operation(
    id="cidr_calculator",
    category="networking",
    name="CIDR Calculator",
    description="Compute network address, broadcast, netmask, and host range for a CIDR block.",
    run=run,
    params=[
        ParamSpec(name="input", label="CIDR", type="text", required=True, help_text="e.g. 10.0.0.0/24"),
    ],
)

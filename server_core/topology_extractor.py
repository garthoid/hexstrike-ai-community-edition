"""
Topology extractor — parses recon tool stdout into a host/port topology graph.

No LLM/AI reasoning involved: this is pure text parsing of output NyxStrike's own
tools already produce, plus a merge step so repeated runs against the same target
update (rather than duplicate) the graph stored on a session.
"""

import re
from typing import Any, Callable, Dict, List, Optional

_HOST_HEADER_RE = re.compile(
    r"Nmap scan report for (?:(?P<hostname>\S+) \((?P<ip_paren>[\da-fA-F:.]+)\)|(?P<ip_plain>[\da-fA-F:.]+))"
)
_PORT_LINE_RE = re.compile(
    r"^(?P<port>\d+)/(?P<protocol>tcp|udp)\s+(?P<state>\S+)\s+(?P<service>\S+)(?:\s+(?P<version>.*))?$"
)
_MAC_LINE_RE = re.compile(r"MAC Address:\s*(?P<mac>\S+)(?:\s+\((?P<vendor>[^)]*)\))?")


def parse_nmap_output(stdout: str) -> Dict[str, List[Dict[str, Any]]]:
    """Parse nmap's default text report into {"hosts": [...], "ports": [...]}.

    Handles multi-host scans (CIDR/range targets) by splitting on each
    "Nmap scan report for ..." header and parsing the port table beneath it.
    """
    hosts: List[Dict[str, Any]] = []
    ports: List[Dict[str, Any]] = []

    if not stdout:
        return {"hosts": hosts, "ports": ports}

    headers = list(_HOST_HEADER_RE.finditer(stdout))
    for i, match in enumerate(headers):
        block_start = match.end()
        block_end = headers[i + 1].start() if i + 1 < len(headers) else len(stdout)
        block = stdout[block_start:block_end]

        ip = match.group("ip_paren") or match.group("ip_plain")
        hostname = match.group("hostname")
        if not ip:
            continue

        mac_match = _MAC_LINE_RE.search(block)
        host_entry: Dict[str, Any] = {"ip": ip}
        if hostname:
            host_entry["hostname"] = hostname
        if mac_match:
            host_entry["mac"] = mac_match.group("mac")
            if mac_match.group("vendor"):
                host_entry["vendor"] = mac_match.group("vendor")
        hosts.append(host_entry)

        for line in block.splitlines():
            port_match = _PORT_LINE_RE.match(line.strip())
            if not port_match:
                continue
            ports.append({
                "host": ip,
                "port": int(port_match.group("port")),
                "protocol": port_match.group("protocol"),
                "state": port_match.group("state"),
                "service": port_match.group("service"),
                "version": (port_match.group("version") or "").strip(),
            })

    return {"hosts": hosts, "ports": ports}


TOPOLOGY_PARSERS: Dict[str, Callable[[str], Dict[str, List[Dict[str, Any]]]]] = {
    "nmap": parse_nmap_output,
    "nmap_advanced": parse_nmap_output,
}


def extract_topology(tool: str, stdout: str) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    """Dispatch to the tool's parser. Returns None if unsupported or nothing found."""
    parser = TOPOLOGY_PARSERS.get(tool)
    if not parser:
        return None
    parsed = parser(stdout or "")
    if not parsed["hosts"] and not parsed["ports"]:
        return None
    return parsed


def merge_topology(
    existing: Optional[Dict[str, Any]],
    new: Dict[str, List[Dict[str, Any]]],
    tool: str,
    ts: int,
) -> Dict[str, Any]:
    """Merge freshly parsed hosts/ports into a session's existing topology.

    Hosts are deduped by IP, ports by (host, port, protocol) with last-write-wins
    on state/service/version. Each host tracks a `sources` list (tool + timestamp)
    for provenance across repeated exports.
    """
    hosts_by_ip: Dict[str, Dict[str, Any]] = {}
    ports_by_key: Dict[tuple, Dict[str, Any]] = {}

    if isinstance(existing, dict):
        for h in existing.get("hosts", []):
            if isinstance(h, dict) and h.get("ip"):
                hosts_by_ip[h["ip"]] = dict(h)
        for p in existing.get("ports", []):
            if isinstance(p, dict) and p.get("host") and p.get("port") is not None:
                key = (p["host"], p["port"], p.get("protocol", "tcp"))
                ports_by_key[key] = dict(p)

    for h in new.get("hosts", []):
        ip = h.get("ip")
        if not ip:
            continue
        current = hosts_by_ip.get(ip, {"ip": ip, "sources": []})
        current.update({k: v for k, v in h.items() if v})
        sources = current.get("sources", [])
        if not isinstance(sources, list):
            sources = []
        sources.append({"tool": tool, "timestamp": ts})
        current["sources"] = sources
        hosts_by_ip[ip] = current

    for p in new.get("ports", []):
        host = p.get("host")
        port = p.get("port")
        if not host or port is None:
            continue
        key = (host, port, p.get("protocol", "tcp"))
        ports_by_key[key] = {**ports_by_key.get(key, {}), **p, "last_seen": ts, "last_tool": tool}

    return {
        "hosts": list(hosts_by_ip.values()),
        "ports": list(ports_by_key.values()),
        "updated_at": ts,
    }

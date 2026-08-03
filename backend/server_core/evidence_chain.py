"""
Evidence Chain — tamper-evident hash chaining for tool run records.

Every recorded tool run (see RunHistoryStore.record) is chained to the
previous run's hash, so a report can prove its evidence wasn't edited
after the fact. Pure functions only — no I/O, no knowledge of where
entries are stored. Callers (RunHistoryStore, session_flow) own storage.

verify_chain() deliberately never assumes the first entry's prev_hash is
GENESIS_HASH: a session's run_log starts wherever the global chain's tip
happened to be when the session began, and RunHistoryStore's own window
may not start at genesis either once old entries are evicted (it's a
capped ring buffer). Genesis only matters to whichever writer chains the
very first run this server has ever recorded.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional

GENESIS_HASH = "0" * 64

_PAYLOAD_FIELDS = (
  "tool",
  "endpoint",
  "params",
  "stdout",
  "stderr",
  "return_code",
  "session_id",
  "timestamp",
)


def _canonical_payload(entry: Dict[str, Any]) -> str:
  payload = {field: entry.get(field) for field in _PAYLOAD_FIELDS}
  return json.dumps(payload, sort_keys=True, default=str)


def compute_hash(entry: Dict[str, Any], prev_hash: str) -> str:
  return hashlib.sha256((prev_hash + _canonical_payload(entry)).encode("utf-8")).hexdigest()


def chain_entry(entry: Dict[str, Any], prev_hash: str) -> Dict[str, Any]:
  """Return a new dict with prev_hash/hash added. Pure — does not mutate entry."""
  return {**entry, "prev_hash": prev_hash, "hash": compute_hash(entry, prev_hash)}


def verify_chain(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
  """Verify a chain of entries, oldest-first.

  Checks each entry's hash is self-consistent with its own stored
  prev_hash + content, and that each entry's prev_hash matches the
  previous entry's hash. Does not assume the first entry's prev_hash is
  GENESIS_HASH — see module docstring.
  """
  total = len(entries)
  verified = 0
  broken_at: Optional[int] = None

  prev_entry_hash: Optional[str] = None
  for idx, entry in enumerate(entries):
    entry_hash = entry.get("hash")
    entry_prev_hash = entry.get("prev_hash")

    if not entry_hash or entry_prev_hash is None:
      broken_at = idx
      break
    if idx > 0 and entry_prev_hash != prev_entry_hash:
      broken_at = idx
      break
    if compute_hash(entry, entry_prev_hash) != entry_hash:
      broken_at = idx
      break

    verified += 1
    prev_entry_hash = entry_hash

  tip_hash = entries[-1].get("hash") if entries else None

  return {
    "valid": broken_at is None,
    "total_runs": total,
    "verified_runs": verified,
    "broken_at_index": broken_at,
    "tip_hash": tip_hash,
  }


def find_run_by_hash(entries: List[Dict[str, Any]], hash_hex: str) -> Optional[Dict[str, Any]]:
  """Search a list of run entries (any order) for a matching hash. Case-insensitive."""
  needle = (hash_hex or "").strip().lower()
  if not needle:
    return None
  for entry in entries:
    if str(entry.get("hash", "")).strip().lower() == needle:
      return entry
  return None

"""
tests/test_evidence_chain.py

Pure-Python unit tests for the tamper-evident hash chain (server_core.evidence_chain),
plus the RunHistoryStore wiring that produces it (record() chaining + hash round-trip
through _load()).

No subprocess, no Flask, no server calls.
"""

import pytest

from server_core.evidence_chain import (
    GENESIS_HASH,
    chain_entry,
    compute_hash,
    find_run_by_hash,
    verify_chain,
)
from server_core.run_history_store import RunHistoryStore


def _make_raw_entry(i: int) -> dict:
    return {
        "tool": f"tool-{i}",
        "endpoint": f"/api/tools/tool-{i}",
        "params": {"target": f"host-{i}"},
        "session_id": "sess_abc",
        "stdout": f"output {i}",
        "stderr": "",
        "return_code": 0,
        "timestamp": f"2026-07-28T00:00:{i:02d}",
    }


def _build_chain(n: int, start_prev_hash: str = GENESIS_HASH) -> list:
    entries = []
    prev_hash = start_prev_hash
    for i in range(n):
        entry = chain_entry(_make_raw_entry(i), prev_hash)
        entries.append(entry)
        prev_hash = entry["hash"]
    return entries


# ---------------------------------------------------------------------------
# chain_entry / compute_hash
# ---------------------------------------------------------------------------

class TestChainEntry:
    def test_chain_entry_adds_hash_and_prev_hash(self):
        entry = chain_entry(_make_raw_entry(0), GENESIS_HASH)
        assert entry["prev_hash"] == GENESIS_HASH
        assert isinstance(entry["hash"], str)
        assert len(entry["hash"]) == 64

    def test_chain_entry_is_pure(self):
        raw = _make_raw_entry(0)
        chain_entry(raw, GENESIS_HASH)
        assert "hash" not in raw and "prev_hash" not in raw

    def test_same_content_same_prev_hash_is_deterministic(self):
        a = chain_entry(_make_raw_entry(0), GENESIS_HASH)
        b = chain_entry(_make_raw_entry(0), GENESIS_HASH)
        assert a["hash"] == b["hash"]

    def test_different_prev_hash_changes_hash(self):
        a = chain_entry(_make_raw_entry(0), GENESIS_HASH)
        b = chain_entry(_make_raw_entry(0), "1" * 64)
        assert a["hash"] != b["hash"]


# ---------------------------------------------------------------------------
# verify_chain
# ---------------------------------------------------------------------------

class TestVerifyChain:
    def test_valid_chain(self):
        entries = _build_chain(5)
        result = verify_chain(entries)
        assert result == {
            "valid": True,
            "total_runs": 5,
            "verified_runs": 5,
            "broken_at_index": None,
            "tip_hash": entries[-1]["hash"],
        }

    def test_empty_chain(self):
        result = verify_chain([])
        assert result["valid"] is True
        assert result["total_runs"] == 0
        assert result["verified_runs"] == 0
        assert result["tip_hash"] is None

    def test_tampered_content_breaks_at_that_index(self):
        entries = _build_chain(5)
        entries[2] = {**entries[2], "stdout": "tampered!"}
        result = verify_chain(entries)
        assert result["valid"] is False
        assert result["broken_at_index"] == 2
        assert result["verified_runs"] == 2

    def test_missing_hash_is_a_break_not_a_crash(self):
        entries = _build_chain(3)
        del entries[1]["hash"]
        result = verify_chain(entries)
        assert result["valid"] is False
        assert result["broken_at_index"] == 1

    def test_no_genesis_assumption_for_subwindow(self):
        """A chain that doesn't start at GENESIS_HASH (e.g. a session that began
        mid-way through global run history) still verifies correctly."""
        entries = _build_chain(4, start_prev_hash="deadbeef" * 8)
        result = verify_chain(entries)
        assert result["valid"] is True
        assert result["verified_runs"] == 4


# ---------------------------------------------------------------------------
# find_run_by_hash
# ---------------------------------------------------------------------------

class TestFindRunByHash:
    def test_finds_known_hash(self):
        entries = _build_chain(4)
        target = entries[2]
        found = find_run_by_hash(entries, target["hash"])
        assert found is target

    def test_case_insensitive(self):
        entries = _build_chain(1)
        found = find_run_by_hash(entries, entries[0]["hash"].upper())
        assert found is entries[0]

    def test_unknown_hash_returns_none(self):
        entries = _build_chain(3)
        assert find_run_by_hash(entries, "0" * 64) is None

    def test_empty_query_returns_none(self):
        entries = _build_chain(3)
        assert find_run_by_hash(entries, "") is None


# ---------------------------------------------------------------------------
# RunHistoryStore wiring
# ---------------------------------------------------------------------------

class TestRunHistoryStoreChaining:
    def test_record_returns_chained_entry_with_genesis_prev_hash(self, tmp_path):
        store = RunHistoryStore(data_dir=str(tmp_path))
        chained = store.record(tool="nmap", endpoint="/api/tools/nmap", params={}, result={"stdout": "ok"})
        assert chained["prev_hash"] == GENESIS_HASH
        assert compute_hash(chained, GENESIS_HASH) == chained["hash"]

    def test_successive_records_chain_together(self, tmp_path):
        store = RunHistoryStore(data_dir=str(tmp_path))
        first = store.record(tool="nmap", endpoint="/e1", params={}, result={"stdout": "a"})
        second = store.record(tool="whois", endpoint="/e2", params={}, result={"stdout": "b"})
        assert second["prev_hash"] == first["hash"]
        # get_all() is newest-first
        assert verify_chain(list(reversed(store.get_all())))["valid"] is True

    def test_chains_onto_genesis_after_legacy_unhashed_entry(self, tmp_path):
        """A store loaded with pre-existing data recorded before this feature shipped
        (hash="" from the _load() fallback) must chain the next record() onto
        GENESIS_HASH, not onto the empty string."""
        store = RunHistoryStore(data_dir=str(tmp_path))
        store._entries.appendleft({
            "id": 1, "tool": "legacy", "endpoint": "", "params": {}, "session_id": "",
            "stdout": "", "stderr": "", "return_code": 0, "success": True,
            "timed_out": False, "partial_results": False, "execution_time": 0.0,
            "timestamp": "", "prev_hash": "", "hash": "",
        })
        chained = store.record(tool="nmap", endpoint="/e1", params={}, result={"stdout": "a"})
        assert chained["prev_hash"] == GENESIS_HASH

    def test_hash_survives_reload(self, tmp_path):
        store = RunHistoryStore(data_dir=str(tmp_path))
        chained = store.record(tool="nmap", endpoint="/e1", params={}, result={"stdout": "a"})

        reloaded = RunHistoryStore(data_dir=str(tmp_path))
        entries = reloaded.get_all()
        assert len(entries) == 1
        assert entries[0]["hash"] == chained["hash"]
        assert entries[0]["prev_hash"] == chained["prev_hash"]

    def test_covers_sessionless_runs_too(self, tmp_path):
        """A run with no session_id still gets chained and is findable by hash —
        the whole point of anchoring the chain in RunHistoryStore, not per-session run_log."""
        store = RunHistoryStore(data_dir=str(tmp_path))
        chained = store.record(tool="nmap", endpoint="/e1", params={}, result={"stdout": "a"}, session_id=None)
        assert chained["session_id"] == ""
        found = find_run_by_hash(store.get_all(), chained["hash"])
        assert found is not None
        assert found["session_id"] == ""

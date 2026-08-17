"""
tests/test_workbench_decloak.py

Pure-Python unit tests for server_core/workbench/decloak.py — the
auto-detect-and-recursively-decode engine backing the Workbench's
Decloak mode. No subprocess, no Flask, no network calls.
"""

from backend.server_core.workbench.decloak import _score, run_decloak


class TestRunDecloak:
    def test_user_example_hex_then_base64_to_plaintext(self):
        result = run_decloak("564739775532566a636d56305132396b5a513d3d")
        assert result["output"] == "TopSecretCode"
        assert result["stopped_reason"] == "plaintext"
        assert [s["operation_id"] for s in result["steps"]] == ["hex", "base64"]
        assert result["steps"][0]["output"] == "VG9wU2VjcmV0Q29kZQ=="

    def test_already_plaintext_returns_unchanged(self):
        result = run_decloak("hello world")
        assert result["steps"] == []
        assert result["output"] == "hello world"
        assert result["stopped_reason"] == "plaintext"

    def test_max_depth_reached(self):
        result = run_decloak("564739775532566a636d56305132396b5a513d3d", max_depth=1)
        assert result["stopped_reason"] == "max_depth"
        assert len(result["steps"]) == 1

    def test_terminal_stop_on_hash_identify_before_hex_decode(self):
        md5_like = "5d41402abc4b2a76b9719d911017c592"
        result = run_decloak(md5_like)
        assert result["steps"][0]["operation_id"] == "hash_identify"
        assert result["stopped_reason"] == "terminal"

    def test_plain_english_not_falsely_rot13d(self):
        result = run_decloak("the quick brown fox jumps over the lazy dog")
        assert result["steps"] == []


class TestScore:
    def test_empty_string_scores_zero(self):
        assert _score("") == 0.0

    def test_readable_text_scores_higher_than_control_bytes(self):
        assert _score("the quick brown fox") > _score("\x01\x02\x03\x04\x05")

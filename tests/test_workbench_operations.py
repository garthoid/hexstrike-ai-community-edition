"""
tests/test_workbench_operations.py

Correctness tests for each Workbench operation's run() function — encoding,
hashing, ciphers, compression, and text utilities. Pure-Python, no subprocess,
no Flask, no network calls, so these are safe/cheap to run on every commit.
"""

import pytest

from server_core.workbench.registry import get_operation


def run(op_id: str, **params) -> dict:
    op = get_operation(op_id)
    assert op is not None, f"operation {op_id!r} not found in registry"
    return op.run(params)


# ---------------------------------------------------------------------------
# encoding
# ---------------------------------------------------------------------------

class TestBase64:
    def test_encode(self):
        assert run("base64", input="hello", mode="encode")["output"] == "aGVsbG8="

    def test_decode(self):
        assert run("base64", input="aGVsbG8=", mode="decode")["output"] == "hello"

    def test_default_mode_is_encode(self):
        assert run("base64", input="hello") == run("base64", input="hello", mode="encode")

    def test_decode_invalid_raises(self):
        with pytest.raises(ValueError):
            run("base64", input="not valid base64!!!", mode="decode")

    def test_unsupported_mode_raises(self):
        with pytest.raises(ValueError):
            run("base64", input="hello", mode="rot13")

    def test_round_trip(self):
        encoded = run("base64", input="round trip me", mode="encode")["output"]
        assert run("base64", input=encoded, mode="decode")["output"] == "round trip me"


class TestBase32:
    def test_encode(self):
        assert run("base32", input="hello", mode="encode")["output"] == "NBSWY3DP"

    def test_decode(self):
        assert run("base32", input="NBSWY3DP", mode="decode")["output"] == "hello"

    def test_decode_invalid_raises(self):
        with pytest.raises(ValueError):
            run("base32", input="!!!not-valid!!!", mode="decode")

    def test_round_trip(self):
        encoded = run("base32", input="round trip me", mode="encode")["output"]
        assert run("base32", input=encoded, mode="decode")["output"] == "round trip me"


class TestHex:
    def test_encode(self):
        assert run("hex", input="hi", mode="encode")["output"] == "6869"

    def test_decode(self):
        assert run("hex", input="6869", mode="decode")["output"] == "hi"

    def test_decode_ignores_whitespace(self):
        assert run("hex", input="68 69\n", mode="decode")["output"] == "hi"

    def test_decode_invalid_raises(self):
        with pytest.raises(ValueError):
            run("hex", input="zz", mode="decode")


class TestUrlEncoding:
    def test_encode_default_leaves_slash(self):
        assert run("url_encoding", input="a b/c", mode="encode")["output"] == "a%20b/c"

    def test_encode_all_encodes_slash(self):
        result = run("url_encoding", input="a b/c", mode="encode", encode_all="true")["output"]
        assert result == "a%20b%2Fc"

    def test_decode(self):
        assert run("url_encoding", input="a%20b%2Fc", mode="decode")["output"] == "a b/c"


class TestHtmlEntities:
    def test_encode(self):
        result = run("html_entities", input='<a href="x">&Test</a>', mode="encode")["output"]
        assert result == "&lt;a href=&quot;x&quot;&gt;&amp;Test&lt;/a&gt;"

    def test_decode(self):
        assert run("html_entities", input="&lt;a&gt;&amp;", mode="decode")["output"] == "<a>&"

    def test_round_trip(self):
        original = '<script>alert("hi")</script>'
        encoded = run("html_entities", input=original, mode="encode")["output"]
        assert run("html_entities", input=encoded, mode="decode")["output"] == original


# ---------------------------------------------------------------------------
# hashing
# ---------------------------------------------------------------------------

class TestHashDigest:
    def test_md5_known_vector(self):
        assert run("hash_digest", input="hello", algorithm="md5")["output"] == "5d41402abc4b2a76b9719d911017c592"

    def test_sha256_known_vector(self):
        expected = "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
        assert run("hash_digest", input="hello", algorithm="sha256")["output"] == expected

    def test_default_algorithm_is_sha256(self):
        assert run("hash_digest", input="hello") == run("hash_digest", input="hello", algorithm="sha256")

    def test_unsupported_algorithm_raises(self):
        with pytest.raises(ValueError):
            run("hash_digest", input="hello", algorithm="md6")


class TestHmacDigest:
    def test_known_vector(self):
        # HMAC-SHA256("key", "The quick brown fox jumps over the lazy dog")
        expected = "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8"
        result = run(
            "hmac_digest",
            input="The quick brown fox jumps over the lazy dog",
            key="key",
            algorithm="sha256",
        )["output"]
        assert result == expected

    def test_different_keys_produce_different_digests(self):
        a = run("hmac_digest", input="msg", key="key1")["output"]
        b = run("hmac_digest", input="msg", key="key2")["output"]
        assert a != b

    def test_unsupported_algorithm_raises(self):
        with pytest.raises(ValueError):
            run("hmac_digest", input="msg", key="k", algorithm="md6")


# ---------------------------------------------------------------------------
# ciphers
# ---------------------------------------------------------------------------

class TestRot13:
    def test_encode(self):
        assert run("rot13", input="hello")["output"] == "uryyb"

    def test_self_inverse(self):
        assert run("rot13", input=run("rot13", input="hello")["output"])["output"] == "hello"


class TestCaesarCipher:
    def test_default_shift(self):
        assert run("caesar_cipher", input="abc")["output"] == "def"

    def test_negative_shift_decodes(self):
        encoded = run("caesar_cipher", input="hello", shift=5)["output"]
        assert run("caesar_cipher", input=encoded, shift=-5)["output"] == "hello"

    def test_non_alpha_passes_through(self):
        assert run("caesar_cipher", input="a-1!", shift=1)["output"] == "b-1!"

    def test_invalid_shift_raises(self):
        with pytest.raises(ValueError):
            run("caesar_cipher", input="abc", shift="not-a-number")


class TestXorCipher:
    def test_empty_key_raises(self):
        with pytest.raises(ValueError):
            run("xor_cipher", input="abc", key="")

    def test_round_trip_via_hex_decode(self):
        # xor_cipher outputs hex; XORing again with the same key recovers the
        # original bytes once the hex is decoded back to raw bytes.
        hex_out = run("xor_cipher", input="secret message", key="k3y")["output"]
        raw = bytes.fromhex(hex_out)
        key_bytes = b"k3y"
        recovered = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(raw))
        assert recovered.decode("utf-8") == "secret message"


# ---------------------------------------------------------------------------
# compression
# ---------------------------------------------------------------------------

class TestGzip:
    def test_round_trip(self):
        compressed = run("gzip", input="a" * 200, mode="compress")["output"]
        assert run("gzip", input=compressed, mode="decompress")["output"] == "a" * 200

    def test_default_mode_is_compress(self):
        assert run("gzip", input="a") == run("gzip", input="a", mode="compress")

    def test_decompress_invalid_raises(self):
        with pytest.raises(ValueError):
            run("gzip", input="not base64 gzip data", mode="decompress")


class TestZlib:
    def test_round_trip(self):
        compressed = run("zlib", input="b" * 200, mode="compress")["output"]
        assert run("zlib", input=compressed, mode="decompress")["output"] == "b" * 200

    def test_decompress_invalid_raises(self):
        with pytest.raises(ValueError):
            run("zlib", input="not base64 zlib data", mode="decompress")


# ---------------------------------------------------------------------------
# analysis
# ---------------------------------------------------------------------------

class TestEntropyCalc:
    def test_empty_input_is_zero(self):
        assert run("entropy_calc", input="")["output"] == "0.0"

    def test_uniform_single_char_is_zero_not_negative_zero(self):
        # Regression: previously rendered "-0.0000 bits/byte" for a
        # single-character alphabet due to floating point rounding.
        output = run("entropy_calc", input="aaaaaaaa")["output"]
        assert not output.startswith("-")
        assert output.startswith("0.0000")

    def test_high_entropy_data_scores_higher_than_low_entropy(self):
        import os

        low = run("entropy_calc", input="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")["output"]
        high = run("entropy_calc", input=os.urandom(64).hex())["output"]
        low_val = float(low.split()[0])
        high_val = float(high.split()[0])
        assert high_val > low_val


class TestJwtDecode:
    def test_decodes_header_and_payload(self):
        # {"alg":"HS256","typ":"JWT"} . {"sub":"1234567890","name":"John Doe"} . <sig>
        token = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
            "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        )
        result = run("jwt_decode", input=token)
        assert '"alg": "HS256"' in result["output"]
        assert '"name": "John Doe"' in result["output"]
        assert "not verified" in result["note"].lower()

    def test_malformed_token_raises(self):
        with pytest.raises(ValueError):
            run("jwt_decode", input="not.a.jwt.at.all")

    def test_bad_segment_raises(self):
        with pytest.raises(ValueError):
            run("jwt_decode", input="not-base64.not-base64.sig")


# ---------------------------------------------------------------------------
# text
# ---------------------------------------------------------------------------

class TestJsonFormat:
    def test_pretty_prints(self):
        output = run("json_format", input='{"b":1,"a":2}', indent=2)["output"]
        assert output == '{\n  "b": 1,\n  "a": 2\n}'

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError):
            run("json_format", input="{not valid")

    def test_invalid_indent_raises(self):
        with pytest.raises(ValueError):
            run("json_format", input="{}", indent="not-a-number")


class TestJsonMinify:
    def test_strips_whitespace(self):
        output = run("json_minify", input='{"b": 1,   "a": [1, 2, 3]}')["output"]
        assert output == '{"b":1,"a":[1,2,3]}'

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError):
            run("json_minify", input="{not valid")


class TestNumberBaseConvert:
    @pytest.mark.parametrize(
        "value,from_base,to_base,expected",
        [
            ("255", "decimal", "hexadecimal", "0xff"),
            ("255", "decimal", "binary", "0b11111111"),
            ("255", "decimal", "octal", "0o377"),
            ("0xff", "hexadecimal", "decimal", "255"),
            ("0b1010", "binary", "decimal", "10"),
        ],
    )
    def test_conversions(self, value, from_base, to_base, expected):
        assert run("number_base_convert", input=value, from_base=from_base, to_base=to_base)["output"] == expected

    def test_invalid_number_raises(self):
        with pytest.raises(ValueError):
            run("number_base_convert", input="zz", from_base="decimal", to_base="hexadecimal")

    def test_unsupported_base_raises(self):
        with pytest.raises(ValueError):
            run("number_base_convert", input="1", from_base="roman", to_base="decimal")


class TestUuidGenerate:
    def test_v4_is_valid_uuid(self):
        import uuid

        output = run("uuid_generate", version="4")["output"]
        assert uuid.UUID(output).version == 4

    def test_unsupported_version_raises(self):
        with pytest.raises(ValueError):
            run("uuid_generate", version="7")

    def test_successive_calls_differ(self):
        a = run("uuid_generate", version="4")["output"]
        b = run("uuid_generate", version="4")["output"]
        assert a != b


class TestRandomStringGenerate:
    def test_length_is_respected(self):
        output = run("random_string_generate", length=32, charset="alphanumeric")["output"]
        assert len(output) == 32

    def test_charset_is_respected(self):
        output = run("random_string_generate", length=64, charset="digits")["output"]
        assert all(c.isdigit() for c in output)

    def test_length_out_of_range_raises(self):
        with pytest.raises(ValueError):
            run("random_string_generate", length=0)
        with pytest.raises(ValueError):
            run("random_string_generate", length=99999)

    def test_unsupported_charset_raises(self):
        with pytest.raises(ValueError):
            run("random_string_generate", length=8, charset="not-a-real-charset")

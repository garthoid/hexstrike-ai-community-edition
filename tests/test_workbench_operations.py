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


class TestBase85:
    def test_round_trip(self):
        encoded = run("base85", input="round trip me", mode="encode")["output"]
        assert run("base85", input=encoded, mode="decode")["output"] == "round trip me"

    def test_default_mode_is_encode(self):
        assert run("base85", input="hello") == run("base85", input="hello", mode="encode")

    def test_decode_invalid_raises(self):
        with pytest.raises(ValueError):
            run("base85", input="\x01\x02not valid", mode="decode")


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
# crypto
# ---------------------------------------------------------------------------

class TestAesCipher:
    def test_gcm_round_trip(self):
        encrypted = run("aes_cipher", input="hello world", mode="encrypt", cipher_mode="GCM", passphrase="secret")["output"]
        result = run("aes_cipher", input=encrypted, mode="decrypt", cipher_mode="GCM", passphrase="secret")["output"]
        assert result == "hello world"

    def test_cbc_round_trip(self):
        encrypted = run("aes_cipher", input="hello world", mode="encrypt", cipher_mode="CBC", passphrase="secret")["output"]
        result = run("aes_cipher", input=encrypted, mode="decrypt", cipher_mode="CBC", passphrase="secret")["output"]
        assert result == "hello world"

    def test_wrong_passphrase_raises(self):
        encrypted = run("aes_cipher", input="hello", mode="encrypt", cipher_mode="GCM", passphrase="right")["output"]
        with pytest.raises(ValueError):
            run("aes_cipher", input=encrypted, mode="decrypt", cipher_mode="GCM", passphrase="wrong")

    def test_empty_passphrase_raises(self):
        with pytest.raises(ValueError):
            run("aes_cipher", input="hello", mode="encrypt", passphrase="")

    def test_successive_encrypts_differ(self):
        # random IV/nonce each time, so ciphertext should not be deterministic
        a = run("aes_cipher", input="hello", mode="encrypt", cipher_mode="GCM", passphrase="k")["output"]
        b = run("aes_cipher", input="hello", mode="encrypt", cipher_mode="GCM", passphrase="k")["output"]
        assert a != b


class TestRsaKeypair:
    def test_generates_pem_private_and_public_key(self):
        output = run("rsa_keypair", key_size="2048")["output"]
        assert "-----BEGIN PRIVATE KEY-----" in output
        assert "-----END PRIVATE KEY-----" in output
        assert "-----BEGIN PUBLIC KEY-----" in output

    def test_unsupported_key_size_raises(self):
        with pytest.raises(ValueError):
            run("rsa_keypair", key_size="1024")


class TestRsaCipher:
    def _keypair(self):
        output = run("rsa_keypair", key_size="2048")["output"]
        priv, _, pub = output.partition("-----END PRIVATE KEY-----")
        return priv + "-----END PRIVATE KEY-----", pub.strip()

    def test_round_trip(self):
        priv, pub = self._keypair()
        encrypted = run("rsa_cipher", input="top secret", mode="encrypt", pem_key=pub)["output"]
        result = run("rsa_cipher", input=encrypted, mode="decrypt", pem_key=priv)["output"]
        assert result == "top secret"

    def test_invalid_pem_key_raises(self):
        with pytest.raises(ValueError):
            run("rsa_cipher", input="hi", mode="encrypt", pem_key="not a pem key")

    def test_empty_pem_key_raises(self):
        with pytest.raises(ValueError):
            run("rsa_cipher", input="hi", mode="encrypt", pem_key="")


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


class TestRegexExtract:
    def test_finds_all_matches(self):
        assert run("regex_extract", input="a1 b2 c3", pattern=r"\d+")["output"] == "1\n2\n3"

    def test_ignorecase_flag(self):
        assert run("regex_extract", input="Hello hello", pattern="hello", flags="i")["output"] == "Hello\nhello"

    def test_no_matches_returns_empty(self):
        assert run("regex_extract", input="abc", pattern=r"\d+")["output"] == ""

    def test_empty_pattern_raises(self):
        with pytest.raises(ValueError):
            run("regex_extract", input="abc", pattern="")

    def test_invalid_pattern_raises(self):
        with pytest.raises(ValueError):
            run("regex_extract", input="abc", pattern="(")


class TestTimestampConvert:
    def test_epoch_to_iso(self):
        assert run("timestamp_convert", input="0", mode="epoch_to_iso")["output"] == "1970-01-01T00:00:00Z"

    def test_iso_to_epoch(self):
        assert run("timestamp_convert", input="1970-01-01T00:00:00Z", mode="iso_to_epoch")["output"] == "0.0"

    def test_round_trip(self):
        iso = run("timestamp_convert", input="1700000000", mode="epoch_to_iso")["output"]
        epoch = run("timestamp_convert", input=iso, mode="iso_to_epoch")["output"]
        assert float(epoch) == 1700000000.0

    def test_non_numeric_epoch_raises(self):
        with pytest.raises(ValueError):
            run("timestamp_convert", input="not-a-number", mode="epoch_to_iso")

    def test_invalid_iso_raises(self):
        with pytest.raises(ValueError):
            run("timestamp_convert", input="not-a-date", mode="iso_to_epoch")


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


class TestCaseConvert:
    def test_upper(self):
        assert run("case_convert", input="hello", mode="upper")["output"] == "HELLO"

    def test_snake_case(self):
        assert run("case_convert", input="Hello World", mode="snake_case")["output"] == "hello_world"

    def test_camel_case(self):
        assert run("case_convert", input="hello world", mode="camelCase")["output"] == "helloWorld"

    def test_unsupported_mode_raises(self):
        with pytest.raises(ValueError):
            run("case_convert", input="hello", mode="kebab_case")


class TestLineTools:
    def test_sort(self):
        assert run("line_tools", input="b\na\nc", mode="sort")["output"] == "a\nb\nc"

    def test_unique_preserves_first_occurrence_order(self):
        assert run("line_tools", input="b\na\nb\nc", mode="unique")["output"] == "b\na\nc"

    def test_reverse(self):
        assert run("line_tools", input="a\nb\nc", mode="reverse")["output"] == "c\nb\na"

    def test_unsupported_mode_raises(self):
        with pytest.raises(ValueError):
            run("line_tools", input="a\nb", mode="shuffle")


# ---------------------------------------------------------------------------
# networking
# ---------------------------------------------------------------------------

class TestCidrCalculator:
    def test_computes_network_details(self):
        output = run("cidr_calculator", input="10.0.0.0/24")["output"]
        assert "Network: 10.0.0.0" in output
        assert "Broadcast: 10.0.0.255" in output
        assert "Usable hosts: 254" in output

    def test_non_strict_host_bits_set(self):
        # strict=False means a host address with bits set is normalized to its network
        output = run("cidr_calculator", input="10.0.0.5/24")["output"]
        assert "Network: 10.0.0.0" in output

    def test_empty_input_raises(self):
        with pytest.raises(ValueError):
            run("cidr_calculator", input="")

    def test_invalid_cidr_raises(self):
        with pytest.raises(ValueError):
            run("cidr_calculator", input="not-a-cidr")

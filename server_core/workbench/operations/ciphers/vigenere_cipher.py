from server_core.workbench.registry import Operation, ParamSpec

MODES = ["encrypt", "decrypt"]


def run(params: dict) -> dict:
    text = params.get("input", "")
    key = params.get("key", "")
    mode = params.get("mode", "encrypt")
    if mode not in MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    key_letters = [ch for ch in key if ch.isalpha()]
    if not key_letters:
        raise ValueError("Key must contain at least one letter")

    sign = 1 if mode == "encrypt" else -1
    out_chars = []
    key_index = 0
    for ch in text:
        if "a" <= ch <= "z":
            shift = (ord(key_letters[key_index % len(key_letters)].lower()) - ord("a")) * sign
            out_chars.append(chr((ord(ch) - ord("a") + shift) % 26 + ord("a")))
            key_index += 1
        elif "A" <= ch <= "Z":
            shift = (ord(key_letters[key_index % len(key_letters)].lower()) - ord("a")) * sign
            out_chars.append(chr((ord(ch) - ord("A") + shift) % 26 + ord("A")))
            key_index += 1
        else:
            out_chars.append(ch)
    return {"output": "".join(out_chars)}


OPERATION = Operation(
    id="vigenere_cipher",
    category="ciphers",
    name="Vigenère Cipher",
    description="Encrypt/decrypt text with a repeating-key Vigenère cipher. Non-letters pass through unchanged; case is preserved.",
    run=run,
    params=[
        ParamSpec(name="input", label="Input", type="textarea", required=True),
        ParamSpec(name="key", label="Key", type="text", required=True, help_text="Non-letter characters in the key are ignored."),
        ParamSpec(name="mode", label="Mode", type="select", choices=MODES, default="encrypt"),
    ],
)

import os
import shlex
import tempfile

from backend.server_core.singletons import ROCKYOU_PATH
from backend.server_core.tool_spec import ParamSpec, ToolSpec, ToolValidationError


def _aircrack_ng_command(p: dict) -> str:
    argv = ["aircrack-ng", *p["capture_files"], "-w", p["wordlist"]]
    if p["bssid"]:
        argv.append("-b")
        argv.append(p["bssid"])
    return shlex.join(argv)


def _write_tmp_hash(p: dict, hash_value: str) -> str:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    tmp.write(hash_value.strip() + "\n")
    tmp.close()
    p["_tmp_file"] = tmp.name
    return tmp.name


def _cleanup_tmp_postprocess(raw, params: dict):
    tmp_file = params.pop("_tmp_file", None)
    if tmp_file and os.path.exists(tmp_file):
        os.unlink(tmp_file)
    return raw


def _hashcat_command(p: dict) -> str:
    hash_file = p["hash_file"]
    hash_value = p["hash"]
    if not hash_file and not hash_value:
        raise ToolValidationError("Either hash_file or hash parameter is required")

    target = hash_file if hash_file else _write_tmp_hash(p, hash_value)

    argv = ["hashcat", "-m", p["hash_type"], "-a", p["attack_mode"], target]
    if p["attack_mode"] == "0" and p["wordlist"]:
        argv.append(p["wordlist"])
    elif p["attack_mode"] == "3" and p["mask"]:
        argv.append(p["mask"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _hashid_command(p: dict) -> str:
    argv = ["hashid", p["hash_value"]]
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _hydra_command(p: dict) -> str:
    if not (p["username"] or p["username_file"]) or not (p["password"] or p["password_file"]):
        raise ToolValidationError("Username/username_file and password/password_file are required")

    argv = ["hydra", "-t", "4"]
    if p["username"]:
        argv.append("-l")
        argv.append(p["username"])
    elif p["username_file"]:
        argv.append("-L")
        argv.append(p["username_file"])
    if p["password"]:
        argv.append("-p")
        argv.append(p["password"])
    elif p["password_file"]:
        argv.append("-P")
        argv.append(p["password_file"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    argv.append(p["target"])
    argv.append(p["service"])
    return shlex.join(argv)


def _john_command(p: dict) -> str:
    argv = ["john"]
    if p["format"]:
        argv.append(f"--format={p['format']}")
    if p["wordlist"]:
        argv.append(f"--wordlist={p['wordlist']}")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    argv.append(p["hash_file"])
    return shlex.join(argv)


def _medusa_command(p: dict) -> str:
    argv = ["medusa", "-h", p["target"], "-M", p["module"]]
    if p["username"]:
        argv.append("-u")
        argv.append(p["username"])
    elif p["username_file"]:
        argv.append("-U")
        argv.append(p["username_file"])
    if p["password"]:
        argv.append("-p")
        argv.append(p["password"])
    elif p["password_file"]:
        argv.append("-P")
        argv.append(p["password_file"])
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _ophcrack_command(p: dict) -> str:
    hash_file = p["hash_file"]
    hash_value = p["hash"]
    if not hash_file and not hash_value:
        raise ToolValidationError("Either hash_file or hash is required")

    if hash_file:
        if not os.path.isfile(hash_file):
            raise ToolValidationError(f"Hash file not found: {hash_file}")
        target = hash_file
    else:
        target = _write_tmp_hash(p, hash_value)

    argv = ["ophcrack", "-g"]
    if p["tables_dir"]:
        if not os.path.isdir(p["tables_dir"]):
            raise ToolValidationError(f"tables_dir not found: {p['tables_dir']}")
        argv.append("-d")
        argv.append(p["tables_dir"])
    if p["tables"]:
        argv.append("-t")
        argv.append(p["tables"])
    argv.append("-f")
    argv.append(target)
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


def _patator_command(p: dict) -> str:
    username, username_file = p["username"], p["username_file"]
    password, password_file = p["password"], p["password_file"]
    if username and username_file:
        raise ToolValidationError("Specify only one of username or username_file")
    if password and password_file:
        raise ToolValidationError("Specify only one of password or password_file")

    argv = ["patator", p["module"], f"host={p['target']}"]
    if username:
        argv.append(f"user={username}")
    elif username_file:
        if not os.path.isfile(username_file):
            raise ToolValidationError(f"username_file not found: {username_file}")
        argv.append(f"user=FILE:{username_file}")
    if password:
        argv.append(f"password={password}")
    elif password_file:
        if not os.path.isfile(password_file):
            raise ToolValidationError(f"password_file not found: {password_file}")
        argv.append(f"password=FILE:{password_file}")
    if p["additional_args"]:
        argv.extend(shlex.split(p["additional_args"]))
    return shlex.join(argv)


SPECS = [
    ToolSpec(
        name="aircrack-ng",
        mcp_tool_name="aircrack_ng_analysis",
        endpoint="/api/tools/password_cracking/aircrack_ng",
        category="password_cracking",
        description="Execute Aircrack-ng for Wi-Fi password cracking.",
        params=[
            ParamSpec("capture_files", list, required=True, help_text="List of capture file paths (.cap, .ivs, etc.)"),
            ParamSpec("wordlist", str, required=True, help_text="Path to a wordlist file"),
            ParamSpec("bssid", str, default="", help_text="Target BSSID (AP MAC address)"),
        ],
        build_command=_aircrack_ng_command,
        use_cache=False,
    ),
    ToolSpec(
        name="hashcat",
        mcp_tool_name="hashcat_crack",
        endpoint="/api/tools/hashcat",
        category="password_cracking",
        description="Execute Hashcat for advanced password cracking.",
        params=[
            ParamSpec("hash_type", str, required=True, help_text="Hash type number for Hashcat"),
            ParamSpec("hash_file", str, default="", help_text="Path to file containing password hashes (takes priority over hash)"),
            ParamSpec("hash", str, default="", help_text="A single hash string to crack (used when hash_file is not provided)"),
            ParamSpec("attack_mode", str, default="0", help_text="Attack mode (0=dict, 1=combo, 3=mask, etc.)"),
            ParamSpec("wordlist", str, default=ROCKYOU_PATH, help_text="Wordlist file for dictionary attacks"),
            ParamSpec("mask", str, default="", help_text="Mask for mask attacks"),
            ParamSpec("additional_args", str, default="", help_text="Additional Hashcat arguments"),
        ],
        build_command=_hashcat_command,
        postprocess=_cleanup_tmp_postprocess,
    ),
    ToolSpec(
        name="hashid",
        mcp_tool_name="hashid",
        endpoint="/api/tools/password_cracking/hashid",
        category="password_cracking",
        description="Identify the type of a given hash value using hashID.",
        params=[
            ParamSpec("hash_value", str, required=True, help_text="The hash string to identify"),
            ParamSpec("additional_args", str, default="", help_text="Extra CLI flags for hashID (e.g., '-m', '-e')"),
        ],
        build_command=_hashid_command,
    ),
    ToolSpec(
        name="hydra",
        mcp_tool_name="hydra_attack",
        endpoint="/api/tools/hydra",
        category="password_cracking",
        description="Execute Hydra for password brute forcing.",
        params=[
            ParamSpec("target", str, required=True, help_text="The target IP or hostname"),
            ParamSpec("service", str, required=True, help_text="The service to attack (ssh, ftp, http, etc.)"),
            ParamSpec("username", str, default="", help_text="Single username to test"),
            ParamSpec("username_file", str, default="", help_text="File containing usernames"),
            ParamSpec("password", str, default="", help_text="Single password to test"),
            ParamSpec("password_file", str, default="", help_text="File containing passwords"),
            ParamSpec("additional_args", str, default="", help_text="Additional Hydra arguments"),
        ],
        build_command=_hydra_command,
    ),
    ToolSpec(
        name="john",
        mcp_tool_name="john_crack",
        endpoint="/api/tools/john",
        category="password_cracking",
        description="Execute John the Ripper for password cracking.",
        params=[
            ParamSpec("hash_file", str, required=True, help_text="File containing password hashes"),
            ParamSpec("wordlist", str, default=ROCKYOU_PATH, help_text="Wordlist file to use"),
            ParamSpec("format", str, default="", help_text="Hash format type"),
            ParamSpec("additional_args", str, default="", help_text="Additional John arguments"),
        ],
        build_command=_john_command,
    ),
    ToolSpec(
        name="medusa",
        mcp_tool_name="medusa_attack",
        endpoint="/api/tools/medusa",
        category="password_cracking",
        description="Execute Medusa for password brute forcing.",
        params=[
            ParamSpec("target", str, required=True, help_text="Target hostname or IP address (maps to -h)"),
            ParamSpec("module", str, required=True, help_text="Medusa module/service to attack (maps to -M)"),
            ParamSpec("username", str, default="", help_text="Single username to test (maps to -u)"),
            ParamSpec("username_file", str, default="", help_text="File with usernames (maps to -U)"),
            ParamSpec("password", str, default="", help_text="Single password to test (maps to -p)"),
            ParamSpec("password_file", str, default="", help_text="File with passwords (maps to -P)"),
            ParamSpec("additional_args", str, default="", help_text="Extra Medusa CLI flags"),
        ],
        build_command=_medusa_command,
    ),
    ToolSpec(
        name="ophcrack",
        mcp_tool_name="ophcrack_crack",
        endpoint="/api/tools/password-cracking/ophcrack",
        category="password_cracking",
        description="Execute Ophcrack for Windows hash cracking.",
        params=[
            ParamSpec("hash_file", str, default="", help_text="Path to the hash file (pwdump/session). Takes priority over hash"),
            ParamSpec("hash", str, default="", help_text="Inline hash string to crack (used when hash_file is not provided)"),
            ParamSpec("tables_dir", str, default="", help_text="Path to rainbow tables directory"),
            ParamSpec("tables", str, default="", help_text="Table set string for -t"),
            ParamSpec("additional_args", str, default="", help_text="Extra ophcrack CLI arguments"),
        ],
        build_command=_ophcrack_command,
        postprocess=_cleanup_tmp_postprocess,
    ),
    ToolSpec(
        name="patator",
        mcp_tool_name="patator_attack",
        endpoint="/api/tools/patator",
        category="password_cracking",
        description="Execute Patator for password brute forcing.",
        params=[
            ParamSpec("module", str, required=True, help_text="Patator module to use (e.g., 'ssh_login', 'ftp_login')"),
            ParamSpec("target", str, required=True, help_text="Target host or address for the attack"),
            ParamSpec("username", str, default="", help_text="Single username to test"),
            ParamSpec("username_file", str, default="", help_text="Path to file containing usernames"),
            ParamSpec("password", str, default="", help_text="Single password to test"),
            ParamSpec("password_file", str, default="", help_text="Path to file containing passwords"),
            ParamSpec("additional_args", str, default="", help_text="Extra Patator command-line arguments"),
        ],
        build_command=_patator_command,
    ),
]

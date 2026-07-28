"""
tests/conftest.py

Session-wide safety net: patch every execution path before any test module
is imported so that no test can ever fire a real tool or subprocess.

Belt (this file) + suspenders (module-level patches in test_endpoints_exist.py).

Patched paths
─────────────
1.  server_core.command_executor.execute_command           — primary tool gateway
2.  server_core.enhanced_command_executor.subprocess       — async/process-pool gateway
3.  server_core.enhanced_process_manager.subprocess        — process manager gateway
4.  server_core.python_env_manager.subprocess              — pip-install gateway
5.  server_api.wifi_pentest.hcxdumptool.subprocess         — direct hcxdumptool BPF calls
6.  server_api.active_directory.impacket_scripts.subprocess — impacket direct calls
7.  server_api.ops.system_monitoring.subprocess            — tool-availability probes
8.  server_core.ai_exploit_generator — imports subprocess locally; covered by module patches above
9.  server_core.singletons.cache                           — cache singleton
10. server_core.singletons.telemetry                       — telemetry singleton
"""

import subprocess
import sys
from unittest.mock import MagicMock, patch


_MOCK_RESULT = {"success": True, "output": "mocked", "returncode": 0}

# Fake CompletedProcess for subprocess.run() calls (python_env_manager)
_MOCK_COMPLETED = MagicMock()
_MOCK_COMPLETED.returncode = 0
_MOCK_COMPLETED.stdout = b"mocked"
_MOCK_COMPLETED.stderr = b""

# Fake Popen for enhanced_command_executor / enhanced_process_manager
_MOCK_POPEN = MagicMock()
_MOCK_POPEN.returncode = 0
_MOCK_POPEN.stdout = MagicMock()
_MOCK_POPEN.stdout.__iter__ = lambda s: iter([])
_MOCK_POPEN.communicate.return_value = (b"mocked", b"")
_MOCK_POPEN.wait.return_value = 0
_MOCK_POPEN.poll.side_effect = lambda: 0
_MOCK_POPEN.__enter__ = lambda s: s
_MOCK_POPEN.__exit__ = MagicMock(return_value=False)

_MOCK_SUBPROCESS = MagicMock(spec=subprocess)
_MOCK_SUBPROCESS.run.return_value = _MOCK_COMPLETED
_MOCK_SUBPROCESS.Popen.return_value = _MOCK_POPEN
_MOCK_SUBPROCESS.PIPE = subprocess.PIPE
_MOCK_SUBPROCESS.STDOUT = subprocess.STDOUT
_MOCK_SUBPROCESS.TimeoutExpired = subprocess.TimeoutExpired
_MOCK_SUBPROCESS.CalledProcessError = subprocess.CalledProcessError

_CACHE_MOCK = MagicMock()
_CACHE_MOCK.get_stats.return_value = {}
_CACHE_MOCK.clear.return_value = None

_TELEMETRY_MOCK = MagicMock()
_TELEMETRY_MOCK.get_stats.return_value = {}
_TELEMETRY_MOCK.stats = {"start_time": 0.0}

_patches = [
    patch("server_core.command_executor.execute_command", return_value=_MOCK_RESULT),
    patch("server_core.enhanced_command_executor.subprocess", _MOCK_SUBPROCESS),
    patch("server_core.enhanced_process_manager.subprocess", _MOCK_SUBPROCESS),
    patch("server_core.python_env_manager.subprocess", _MOCK_SUBPROCESS),
    patch("server_core.tool_specs.wifi_pentest.subprocess", _MOCK_SUBPROCESS),
    patch("server_api.active_directory.impacket_scripts.subprocess", _MOCK_SUBPROCESS),
    patch("server_api.ops.system_monitoring.subprocess", _MOCK_SUBPROCESS),
    patch("server_core.singletons.cache", _CACHE_MOCK),
    patch("server_core.singletons.telemetry", _TELEMETRY_MOCK),
]


def pytest_configure(config):
    """Start all patches before test collection begins."""
    for p in _patches:
        p.start()

    from nyxstrike_server import app as _app
    from server_core.plugin_loader import _load_tool_plugin

    if "_plugin_tool_server_api_h2csmuggler" not in sys.modules:
        _load_tool_plugin(_app, "h2csmuggler", set(), set())


def pytest_unconfigure(config):
    """Stop all patches after the session ends."""
    for p in reversed(_patches):
        try:
            p.stop()
        except RuntimeError:
            pass

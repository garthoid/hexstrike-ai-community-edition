import logging
import re
import sys
import backend.server_core.config_core as config_core
from backend.server_core.colored_formatter import ColoredFormatter

_ANSI_ESCAPE = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
_CLF_ACCESS = re.compile(r' - \[\d{2}/\w+/\d{4} \d{2}:\d{2}:\d{2}\]| -\s*$')

_HTTP_ACCESS_LINE = re.compile(r'"[A-Z]+ [^ ]+ HTTP/1\.1[^"]*"\s*\d{3}\b')
_STATUS_304 = re.compile(r'"[A-Z]+ [^ ]+ HTTP/1\.1[^"]*" 304\b')

class _StripCLFNoise(logging.Filter):
    """Remove redundant CLF timestamp and trailing dash from Werkzeug access log lines."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if _STATUS_304.search(msg):
            return False
        if _HTTP_ACCESS_LINE.search(msg) and not config_core.get("SHOW_HTTP_ACCESS_LOGS", False):
            return False
        clean = _CLF_ACCESS.sub('', msg)
        record.msg = clean
        record.args = None
        return True

class _PlainFormatter(logging.Formatter):
    """Formatter that strips ANSI escape codes — safe for log files and grep."""

    def format(self, record):
        formatted = super().format(record)
        return _ANSI_ESCAPE.sub('', formatted)

def setup_logging(log_file: str = 'nyxstrike.log') -> logging.Logger:
    """Setup enhanced logging: colored console output + ANSI-stripped file output."""
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    # Clear existing handlers to avoid duplicate entries on re-call
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    fmt = ColoredFormatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    fmt._stream = console_handler.stream
    console_handler.setFormatter(fmt)
    root.addHandler(console_handler)

    # File handler — plain text, no ANSI codes
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(_PlainFormatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        root.addHandler(file_handler)
    except PermissionError:
        root.warning("Could not open log file %s — logging to console only.", log_file)

    # Strip redundant CLF timestamp and trailing dash from Werkzeug access log lines
    logging.getLogger('werkzeug').addFilter(_StripCLFNoise())

    # Suppress Werkzeug's startup banner lines (e.g. "Serving Flask app",
    # "Development server" warning, "Running on ...").
    class _SuppressWerkzeugBanner(logging.Filter):
        _BANNER_PREFIXES = ('WARNING: This is a development server',)

        def filter(self, record: logging.LogRecord) -> bool:
            msg = record.getMessage()
            return not any(msg.__contains__(p) for p in self._BANNER_PREFIXES)

    logging.getLogger('werkzeug').addFilter(_SuppressWerkzeugBanner())

    return root

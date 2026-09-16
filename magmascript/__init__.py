"""magmascript — a scripting toolkit with domain-first subcommands."""

# The version lives in pyproject.toml alone. It was also a literal here, and the
# two drifted: 3.2.3 shipped reporting itself as 3.2.2, in the REPL banner and
# in the MCP client's User-Agent.
from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("magmascript")
except _PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "0+unknown"

from magmascript.core.config import Config, GHConfig, MediaConfig, MC1Config, PIConfig, get_config, load_config, set_config
from magmascript.core.registry import get_domain, list_domains, register_domain
from magmascript.core.rpc import RPCClient, RPCError, RPCResponse
from magmascript.core.runner import CommandRunner
from magmascript.core.output import format_output, format_table, format_json

# Import domains to trigger registration
from magmascript import domains  # noqa: F401

# Convenience: expose clients at top level
from magmascript.domains.mcp import MCPClient
from magmascript.domains.pi import PIClient
from magmascript.domains.mc1 import MC1Client
from magmascript.domains.mac import MacClient
from magmascript.domains.gh import GHClient
from magmascript.domains.media import MediaClient
from magmascript.domains.rights import RightsClient

# Language module
from magmascript import lang  # noqa: F401

__all__ = [
    "__version__",
    "CommandRunner",
    "Config",
    "GHClient",
    "GHConfig",
    "MC1Client",
    "MacClient",
    "MCPClient",
    "MediaClient",
    "MediaConfig",
    "PIClient",
    "PIConfig",
    "RightsClient",
    "RPCClient",
    "RPCError",
    "RPCResponse",
    "format_output",
    "format_json",
    "format_table",
    "get_config",
    "get_domain",
    "lang",
    "list_domains",
    "load_config",
    "register_domain",
    "set_config",
]

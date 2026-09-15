"""Open Issue Format (OIF) reference tooling. Spec: https://oif.md"""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("oifmd")
except PackageNotFoundError:          # running from a source tree, not installed
    __version__ = "0+unknown"

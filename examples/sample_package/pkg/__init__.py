"""Top-level package for sample_package."""

# Defined before the imports below because pkg/utils/strings.py imports it
# with `from .. import VERSION` while this package is still initializing.
VERSION = "0.1.0"

from .core import run  # noqa: E402

__all__ = ["VERSION", "run"]

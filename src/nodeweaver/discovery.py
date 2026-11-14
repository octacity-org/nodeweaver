"""Find the source files to analyze in a directory tree."""

import os
from pathlib import Path

# Directories that never contain project source code. They are skipped by name
# at any depth, and the walk does not enter them.
EXCLUDED_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "build",
        "dist",
    }
)


def find_python_files(root: str | Path) -> list[str]:
    """Return the `.py` files under `root`, sorted.

    Paths are relative to `root` and use "/" on every operating system, like
    `FileIR.file` (see `ir.py`). Symbolic links to directories are not
    followed, so a link cannot make the walk loop.
    """
    root = Path(root)
    found = []
    # followlinks=False is the default; it is written out because it is a decision.
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        # Prune in place so os.walk does not enter excluded directories at all.
        dirnames[:] = [name for name in dirnames if name not in EXCLUDED_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                path = Path(dirpath, filename).relative_to(root)
                found.append(path.as_posix())
    return sorted(found)

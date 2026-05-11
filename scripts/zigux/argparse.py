from __future__ import annotations

import builtins
import importlib.util
import sysconfig
from pathlib import Path

# Generated validator constants currently embed JSON-style literals.
# Seed lowercase aliases before handing off to the real stdlib module.
for name, value in (("true", True), ("false", False), ("null", None)):
    if not hasattr(builtins, name):
        setattr(builtins, name, value)

_stdlib_path = Path(sysconfig.get_path("stdlib")) / "argparse.py"
_spec = importlib.util.spec_from_file_location(__name__, _stdlib_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load stdlib argparse from {_stdlib_path}")

_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
globals().update(_module.__dict__)

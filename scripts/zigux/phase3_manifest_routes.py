#!/usr/bin/env python3
"""Shared manifest-route parsing helpers for Phase 3 tooling."""

from __future__ import annotations

import json
from pathlib import Path
import shlex


def load_manifest_python_routes(
    repo_root: Path,
    manifest_path: Path,
    *,
    want_selftest: bool,
    ignored_scripts: set[Path] | frozenset[Path],
) -> tuple[set[tuple[Path, tuple[str, ...]]], list[str]]:
    manifest_abspath = repo_root / manifest_path
    if not manifest_abspath.is_file():
        return set(), [f"missing phase3 manifest: {manifest_path.as_posix()}"]

    try:
        manifest = json.loads(manifest_abspath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return set(), [f"invalid phase3 manifest JSON: {manifest_path.as_posix()}: {exc}"]

    replay_routes = manifest.get("replay_routes")
    if not isinstance(replay_routes, list):
        return set(), []

    expected: set[tuple[Path, tuple[str, ...]]] = set()
    for route in replay_routes:
        if not isinstance(route, str):
            continue
        parts = shlex.split(route)
        if len(parts) < 2 or parts[0] != "python3":
            continue
        args = tuple(parts[2:])
        has_selftest = "--self-test" in args
        if want_selftest != has_selftest:
            continue
        script_path = Path(parts[1])
        if script_path.parts[:2] != ("scripts", "zigux") or script_path.suffix != ".py":
            continue
        if script_path in ignored_scripts:
            continue
        expected.add((script_path, args))
    return expected, []

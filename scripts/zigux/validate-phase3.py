#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import tempfile

from phase3_catalog import (
    Phase3Paths,
    audit_phase3_slug_sanity,
    artifact_diff_phase3_lines,
    discover_phase3_slug_rename_candidates,
    discover_phase3_slices,
)
from phase3_check_lib import legacy_wrapper_gate_for_slug, render_wrapper_stub, shared_runner_gate_for_slug


ROOT = Path(__file__).resolve().parents[2]


def _is_legacy_wrapper_manifest_file(rel: str) -> bool:
    return rel.startswith("scripts/zigux/check-phase3-") and rel.endswith(".py")


def validate_manifest(root: Path, path: Path | None, slug: str, issues: list[str]) -> dict[str, object] | None:
    if path is None:
        issues.append(f"{slug}:missing_manifest")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"{slug}:missing_manifest:{path.relative_to(root).as_posix()}")
        return None
    except json.JSONDecodeError as exc:
        issues.append(f"{slug}:invalid_manifest:{path.relative_to(root).as_posix()}:{exc.msg}")
        return None

    if data.get("phase") != "Phase 3":
        issues.append(f"{slug}:manifest_phase={data.get('phase')}")
    if not isinstance(data.get("status"), str) or not data["status"]:
        issues.append(f"{slug}:manifest_status={data.get('status')}")
    if not isinstance(data.get("slice"), str) or not data["slice"]:
        issues.append(f"{slug}:manifest_slice={data.get('slice')}")
    files = data.get("files")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        issues.append(f"{slug}:manifest_files={type(files).__name__}")
        return data
    file_count = data.get("file_count")
    if file_count != len(files):
        issues.append(f"{slug}:manifest_file_count={file_count}")
    for rel in files:
        if _is_legacy_wrapper_manifest_file(rel):
            issues.append(f"{slug}:manifest_legacy_wrapper_file={rel}")
        if not (root / rel).exists():
            issues.append(f"{slug}:manifest_missing_file={rel}")
    return data



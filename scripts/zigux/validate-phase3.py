#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

from phase3_catalog import discover_phase3_slices


ROOT = Path(__file__).resolve().parents[2]


def validate_manifest(path: Path | None, slug: str, issues: list[str]) -> dict[str, object] | None:
    if path is None:
        issues.append(f"{slug}:missing_manifest")
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        issues.append(f"{slug}:missing_manifest:{path.relative_to(ROOT).as_posix()}")
        return None
    except json.JSONDecodeError as exc:
        issues.append(f"{slug}:invalid_manifest:{path.relative_to(ROOT).as_posix()}:{exc.msg}")
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
        if not (ROOT / rel).exists():
            issues.append(f"{slug}:manifest_missing_file={rel}")
    return data


def validate_doc_markers(doc_path: Path, slug: str, manifest: dict[str, object] | None, issues: list[str]) -> None:
    if not doc_path.exists():
        issues.append(f"{slug}:missing_doc:{doc_path.relative_to(ROOT).as_posix()}")
        return
    doc = doc_path.read_text(encoding="utf-8")
    expected = [
        "PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py",
        f"PHASE3_INTEROP_GATE=python3 scripts/zigux/check-phase3-{slug}.py",
        "PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig",
    ]
    if manifest:
        expected.insert(0, f"PHASE3_STATUS={manifest.get('status')}")
        expected.insert(1, f"PHASE3_SLICE={manifest.get('slice')}")
    for marker in expected:
        if marker not in doc:
            issues.append(f"{slug}:missing_doc_marker={marker}")


def main() -> int:
    issues: list[str] = []
    slices = discover_phase3_slices()

    for entry in slices:
        required = {
            "check_script": entry.check_script,
            "dump": entry.dump_path,
            "fixture_dir": entry.fixture_dir,
            "expected": entry.expected_path,
            "harness": entry.harness_path,
        }
        for label, path in required.items():
            if not path.exists():
                issues.append(f"{entry.slug}:missing_{label}:{path.relative_to(ROOT).as_posix()}")

        manifest = validate_manifest(entry.manifest_path, entry.slug, issues)
        validate_doc_markers(entry.doc_path, entry.slug, manifest, issues)

    if issues:
        print("PHASE3_VALIDATION=fail")
        print("MISSING_PHASE3_MARKERS_START")
        for issue in issues:
            print(issue)
        print("MISSING_PHASE3_MARKERS_END")
        return 1

    print("PHASE3_VALIDATION=pass")
    print(f"PHASE3_SLICE_COUNT={len(slices)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

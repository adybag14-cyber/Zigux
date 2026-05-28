#!/usr/bin/env python3
"""Guard the current Phase 2 bootstrap-helper packet."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_tool_manifest.json")
VALIDATOR = Path("scripts/zigux/validate-phase2.py")
BOOTSTRAP_NOTES = Path("Documentation/zigux/phase2-toolchain-bootstrap-notes.md")

BOOTSTRAP_HELPERS = (
    "scripts/zigux/install-zig.py",
    "scripts/zigux/stage-pinned-zig-archive.py",
)

REQUIRED_NOTE_MARKERS = (
    "`scripts/zigux/install-zig.py`",
    "`scripts/zigux/stage-pinned-zig-archive.py`",
)

REQUIRED_VALIDATOR_MARKERS = (
    '"scripts/zigux/install-zig.py",',
    '"scripts/zigux/stage-pinned-zig-archive.py",',
)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json_dict(path: Path) -> dict:
    try:
        payload = json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"invalid json shape in required file: {path}")
    return payload


def find_duplicates(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    manifest = read_json_dict(root / MANIFEST)
    validator_text = read_text(root / VALIDATOR)
    bootstrap_notes = read_text(root / BOOTSTRAP_NOTES)

    present_surfaces = manifest.get("present_surfaces")
    if not isinstance(present_surfaces, dict):
        return [("MISSING_PRESENT_SURFACES", "present_surfaces")]

    helpers = present_surfaces.get("bootstrap_helpers")
    if not isinstance(helpers, list):
        return [("MISSING_BOOTSTRAP_HELPERS", "bootstrap_helpers")]

    non_strings = [repr(entry) for entry in helpers if not isinstance(entry, str)]
    for entry in non_strings:
        issues.append(("INVALID_BOOTSTRAP_HELPER_ENTRY", entry))

    string_helpers = [entry for entry in helpers if isinstance(entry, str)]
    for entry in find_duplicates(string_helpers):
        issues.append(("DUPLICATE_BOOTSTRAP_HELPER_ENTRY", entry))

    for helper in BOOTSTRAP_HELPERS:
        if helper not in string_helpers:
            issues.append(("MISSING_BOOTSTRAP_HELPER_ENTRY", helper))

    for helper in string_helpers:
        if helper not in BOOTSTRAP_HELPERS:
            issues.append(("UNEXPECTED_BOOTSTRAP_HELPER_ENTRY", helper))
        elif not (root / helper).exists():
            issues.append(("MISSING_BOOTSTRAP_HELPER_PATH", helper))

    if string_helpers != list(BOOTSTRAP_HELPERS):
        issues.append(("BOOTSTRAP_HELPER_ORDER_MISMATCH", "bootstrap_helpers"))

    for marker in REQUIRED_VALIDATOR_MARKERS:
        count = validator_text.count(marker)
        if count == 0:
            issues.append(("MISSING_VALIDATOR_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_VALIDATOR_MARKER", f"{marker}:count={count}"))

    for marker in REQUIRED_NOTE_MARKERS:
        count = bootstrap_notes.count(marker)
        if count == 0:
            issues.append(("MISSING_NOTE_MARKER", marker))
        elif count != 1:
            issues.append(("DUPLICATE_NOTE_MARKER", f"{marker}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_BOOTSTRAP_HELPER_SURFACE=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_manifest() -> str:
    payload = {
        "phase": "Phase 2",
        "present_surfaces": {
            "bootstrap_helpers": list(BOOTSTRAP_HELPERS),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def build_validator() -> str:
    lines = [
        "REQUIRED_PATHS = (",
        '    "Documentation/zigux/phase2-toolchain-bootstrap-notes.md",',
        '    "scripts/zigux/install-zig.py",',
        '    "scripts/zigux/stage-pinned-zig-archive.py",',
        ")",
        "",
    ]
    return "\n".join(lines)


def build_bootstrap_notes() -> str:
    lines = [
        "# Phase 2 Toolchain Bootstrap Notes",
        "",
        "- `scripts/zigux/install-zig.py` is directly readable on current `master` and keeps the pinned-channel archive download path explicit.",
        "- `scripts/zigux/stage-pinned-zig-archive.py` is directly readable on current `master` and keeps the staged repo-local archive materialization path explicit.",
        "",
    ]
    return "\n".join(lines)


def build_sample_root(root: Path) -> None:
    for child in root.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()
    write_text(root / MANIFEST, build_manifest())
    write_text(root / VALIDATOR, build_validator())
    write_text(root / BOOTSTRAP_NOTES, build_bootstrap_notes())
    for helper in BOOTSTRAP_HELPERS:
        write_text(root / helper, "present\n")


def run_self_test() -> int:
    expected_case_count = 14
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_bootstrap_helper_surface_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        manifest = read_json_dict(root / MANIFEST)
        del manifest["present_surfaces"]["bootstrap_helpers"]
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("MISSING_BOOTSTRAP_HELPERS", "bootstrap_helpers") in collect_issues(root)
        checks_run += 1

        for helper in BOOTSTRAP_HELPERS:
            build_sample_root(root)
            manifest = read_json_dict(root / MANIFEST)
            manifest["present_surfaces"]["bootstrap_helpers"].remove(helper)
            write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
            assert ("MISSING_BOOTSTRAP_HELPER_ENTRY", helper) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        manifest = read_json_dict(root / MANIFEST)
        manifest["present_surfaces"]["bootstrap_helpers"].append(BOOTSTRAP_HELPERS[0])
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("DUPLICATE_BOOTSTRAP_HELPER_ENTRY", BOOTSTRAP_HELPERS[0]) in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = read_json_dict(root / MANIFEST)
        manifest["present_surfaces"]["bootstrap_helpers"].append("scripts/zigux/unexpected.py")
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("UNEXPECTED_BOOTSTRAP_HELPER_ENTRY", "scripts/zigux/unexpected.py") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest = read_json_dict(root / MANIFEST)
        manifest["present_surfaces"]["bootstrap_helpers"][0], manifest["present_surfaces"]["bootstrap_helpers"][1] = (
            manifest["present_surfaces"]["bootstrap_helpers"][1],
            manifest["present_surfaces"]["bootstrap_helpers"][0],
        )
        write_text(root / MANIFEST, json.dumps(manifest, indent=2) + "\n")
        assert ("BOOTSTRAP_HELPER_ORDER_MISMATCH", "bootstrap_helpers") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        (root / BOOTSTRAP_HELPERS[0]).unlink()
        assert ("MISSING_BOOTSTRAP_HELPER_PATH", BOOTSTRAP_HELPERS[0]) in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_VALIDATOR_MARKERS:
            build_sample_root(root)
            validator_path = root / VALIDATOR
            validator_path.write_text(validator_path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_VALIDATOR_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        validator_path = root / VALIDATOR
        marker = REQUIRED_VALIDATOR_MARKERS[0]
        validator_path.write_text(
            validator_path.read_text(encoding="utf-8").replace(marker, f"{marker}\n{marker}", 1),
            encoding="utf-8",
        )
        assert ("DUPLICATE_VALIDATOR_MARKER", f"{marker}:count=2") in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            build_sample_root(root)
            notes_path = root / BOOTSTRAP_NOTES
            notes_path.write_text(notes_path.read_text(encoding="utf-8").replace(marker, "", 1), encoding="utf-8")
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        build_sample_root(root)
        notes_path = root / BOOTSTRAP_NOTES
        marker = REQUIRED_NOTE_MARKERS[0]
        notes_path.write_text(
            notes_path.read_text(encoding="utf-8").replace(marker, f"{marker} {marker}", 1),
            encoding="utf-8",
        )
        assert ("DUPLICATE_NOTE_MARKER", f"{marker}:count=2") in collect_issues(root)
        checks_run += 1

    assert checks_run == expected_case_count
    print("PHASE2_BOOTSTRAP_HELPER_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_BOOTSTRAP_HELPER_SURFACE_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Keep the Phase 2 bootstrap-helper packet aligned.")
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    parser.add_argument("--write-sample-root", type=Path, help="Write a current-like sample root and exit")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        args.write_sample_root.mkdir(parents=True, exist_ok=True)
        build_sample_root(args.write_sample_root.resolve())
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    print("PHASE2_BOOTSTRAP_HELPER_SURFACE=pass")
    print(f"PHASE2_BOOTSTRAP_HELPER_SURFACE_COUNT={len(BOOTSTRAP_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

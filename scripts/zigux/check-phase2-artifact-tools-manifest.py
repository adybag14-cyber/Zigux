#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) >= 3 else Path.cwd()
MANIFEST = Path("zigux/tests/fixtures/phase2_artifact_tools_manifest.json")

REQUIRED_TOP_LEVEL = {
    "phase": "Phase 2",
    "status": "active",
    "scope": "artifact-diff support for fixture-backed scripts/zigux validation",
}

REQUIRED_TOOLING = {
    "primary": ["scripts/zigux/artifact_diff.py"],
    "consumers": [
        "scripts/zigux/check-kconfig-bridge.py",
        "scripts/zigux/check-fixdep-diff.py",
    ],
    "checkers": ["scripts/zigux/check-phase2-artifact-tools-manifest.py"],
    "supported_modes": ["json", "text", "bytes"],
}

REQUIRED_NOTE_MARKERS = (
    "The artifact diff helper provides deterministic comparison output for fixture-backed scripts-root checks in both the kconfig bridge and fixdep parity packets.",
    "Keep `scripts/zigux/check-phase2-artifact-tools-manifest.py` explicit so the bounded Phase 2 artifact-support manifest fails closed beside the broader Phase 2 tool packet.",
    "Keep future Phase 2 artifact-diff follow-up bounded to live consumers like `scripts/zigux/check-kconfig-bridge.py` and `scripts/zigux/check-fixdep-diff.py` plus directly readable fixture packets before widening into broader closure routes.",
)


def read_manifest(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def find_duplicate_strings(entries: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for entry in entries:
        if entry in seen and entry not in duplicates:
            duplicates.append(entry)
        seen.add(entry)
    return duplicates


def collect_issues(root: Path) -> list[tuple[str, str]]:
    manifest = read_manifest(root / MANIFEST)
    issues: list[tuple[str, str]] = []

    for key, expected in REQUIRED_TOP_LEVEL.items():
        if manifest.get(key) != expected:
            issues.append(("TOP_LEVEL_MISMATCH", key))

    tooling = manifest.get("tooling")
    if not isinstance(tooling, dict):
        issues.append(("MISSING_TOOLING", "tooling"))
    else:
        for key, expected in REQUIRED_TOOLING.items():
            entries = tooling.get(key)
            if not isinstance(entries, list):
                issues.append(("INVALID_TOOLING_LIST", key))
                continue
            non_string_entries = [repr(entry) for entry in entries if not isinstance(entry, str)]
            for entry in non_string_entries:
                issues.append(("INVALID_TOOLING_ENTRY", f"{key}:{entry}"))
            string_entries = [entry for entry in entries if isinstance(entry, str)]
            for entry in find_duplicate_strings(string_entries):
                issues.append(("DUPLICATE_TOOLING_ENTRY", f"{key}:{entry}"))
            if non_string_entries or string_entries != expected:
                issues.append(("TOOLING_MISMATCH", key))

    notes = manifest.get("notes")
    if not isinstance(notes, list):
        issues.append(("MISSING_NOTES", "notes"))
    else:
        non_string_notes = [repr(note) for note in notes if not isinstance(note, str)]
        for note in non_string_notes:
            issues.append(("INVALID_NOTE_ENTRY", note))
        string_notes = [note for note in notes if isinstance(note, str)]
        for marker in find_duplicate_strings(string_notes):
            issues.append(("DUPLICATE_NOTE_ENTRY", marker))
        for marker in REQUIRED_NOTE_MARKERS:
            if marker not in string_notes:
                issues.append(("MISSING_NOTE_MARKER", marker))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)
    print("PHASE2_ARTIFACT_TOOLS_MANIFEST=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def write_manifest(path: Path, manifest: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def build_self_test_manifest() -> dict:
    return {
        **REQUIRED_TOP_LEVEL,
        "tooling": {key: list(entries) for key, entries in REQUIRED_TOOLING.items()},
        "notes": list(REQUIRED_NOTE_MARKERS),
    }


def run_self_test() -> int:
    expected_case_count = (
        1
        + len(REQUIRED_TOP_LEVEL)
        + 1
        + len(REQUIRED_TOOLING)
        + sum(len(entries) for entries in REQUIRED_TOOLING.values())
        + len(REQUIRED_TOOLING)
        + len(REQUIRED_TOOLING)
        + 1
        + len(REQUIRED_NOTE_MARKERS)
        + 1
        + 1
        + 1
    )
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_artifact_tools_manifest_") as tmp_dir:
        root = Path(tmp_dir)
        manifest_path = root / MANIFEST

        write_manifest(manifest_path, build_self_test_manifest())
        assert collect_issues(root) == []
        checks_run += 1

        for key in REQUIRED_TOP_LEVEL:
            manifest = build_self_test_manifest()
            manifest[key] = "broken"
            write_manifest(manifest_path, manifest)
            assert ("TOP_LEVEL_MISMATCH", key) in collect_issues(root)
            checks_run += 1

        manifest = build_self_test_manifest()
        manifest["tooling"] = "broken"
        write_manifest(manifest_path, manifest)
        assert ("MISSING_TOOLING", "tooling") in collect_issues(root)
        checks_run += 1

        for key, expected in REQUIRED_TOOLING.items():
            manifest = build_self_test_manifest()
            manifest["tooling"][key] = "broken"
            write_manifest(manifest_path, manifest)
            assert ("INVALID_TOOLING_LIST", key) in collect_issues(root)
            checks_run += 1

            for entry in expected:
                manifest = build_self_test_manifest()
                manifest["tooling"][key].remove(entry)
                write_manifest(manifest_path, manifest)
                assert ("TOOLING_MISMATCH", key) in collect_issues(root)
                checks_run += 1

            manifest = build_self_test_manifest()
            manifest["tooling"][key].append(expected[0])
            write_manifest(manifest_path, manifest)
            issues = collect_issues(root)
            assert ("DUPLICATE_TOOLING_ENTRY", f"{key}:{expected[0]}") in issues
            assert ("TOOLING_MISMATCH", key) in issues
            checks_run += 1

            manifest = build_self_test_manifest()
            manifest["tooling"][key].append(123)
            write_manifest(manifest_path, manifest)
            issues = collect_issues(root)
            assert ("INVALID_TOOLING_ENTRY", f"{key}:123") in issues
            assert ("TOOLING_MISMATCH", key) in issues
            checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"] = "broken"
        write_manifest(manifest_path, manifest)
        assert ("MISSING_NOTES", "notes") in collect_issues(root)
        checks_run += 1

        for marker in REQUIRED_NOTE_MARKERS:
            manifest = build_self_test_manifest()
            manifest["notes"].remove(marker)
            write_manifest(manifest_path, manifest)
            assert ("MISSING_NOTE_MARKER", marker) in collect_issues(root)
            checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"].append(REQUIRED_NOTE_MARKERS[0])
        write_manifest(manifest_path, manifest)
        assert ("DUPLICATE_NOTE_ENTRY", REQUIRED_NOTE_MARKERS[0]) in collect_issues(root)
        checks_run += 1

        manifest = build_self_test_manifest()
        manifest["notes"].append(123)
        write_manifest(manifest_path, manifest)
        assert ("INVALID_NOTE_ENTRY", "123") in collect_issues(root)
        checks_run += 1

        manifest_path.unlink()
        try:
            collect_issues(root)
        except SystemExit as exc:
            assert "required file missing" in str(exc)
            checks_run += 1
        else:
            raise AssertionError("missing manifest did not abort")

    assert checks_run == expected_case_count
    print("PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST=pass")
    print(f"PHASE2_ARTIFACT_TOOLS_MANIFEST_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Keep the Phase 2 artifact-tools manifest aligned with the current artifact-diff packet."
    )
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--self-test", action="store_true", help="Run the built-in contract self-test")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)
    print("PHASE2_ARTIFACT_TOOLS_MANIFEST=pass")
    print(f"PHASE2_ARTIFACT_TOOLS_MANIFEST_REQUIRED_NOTE_COUNT={len(REQUIRED_NOTE_MARKERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

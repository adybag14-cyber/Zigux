#!/usr/bin/env python3
"""Fail closed when the Phase 2 bridge-helper manifest surface drifts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


MANIFEST_PATH = Path("zigux/tests/fixtures/phase2_tool_manifest.json")

EXPECTED_BRIDGE_HELPERS = (
    "scripts/zigux/kconfig/conf_bridge.zig",
    "scripts/zigux/kconfig/confdata_bridge.zig",
    "scripts/zigux/genksyms.zig",
    "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig",
    "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _sample_manifest(entries: list[object] | None = None) -> str:
    payload = {
        "phase": "Phase 2",
        "status": "active",
        "present_surfaces": {
            "bridge_helpers": list(
                EXPECTED_BRIDGE_HELPERS if entries is None else entries
            ),
        },
    }
    return json.dumps(payload, indent=2) + "\n"


def count_exact_entries(entries: list[str], marker: str) -> int:
    return sum(1 for entry in entries if entry == marker)


def validate(repo_root: Path) -> list[str]:
    manifest_path = repo_root / MANIFEST_PATH
    if not manifest_path.is_file():
        return [f"missing manifest file: {MANIFEST_PATH.as_posix()}"]

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"invalid manifest json: {exc.msg}"]

    surfaces = manifest.get("present_surfaces")
    if not isinstance(surfaces, dict):
        return ["invalid present_surfaces object"]

    bridge_helpers = surfaces.get("bridge_helpers")
    if not isinstance(bridge_helpers, list):
        return ["invalid bridge_helpers list"]

    issues: list[str] = []
    for index, entry in enumerate(bridge_helpers):
        if not isinstance(entry, str):
            issues.append(f"invalid bridge_helpers entry at index {index}: {entry!r}")

    string_entries = [entry for entry in bridge_helpers if isinstance(entry, str)]
    if len(bridge_helpers) != len(EXPECTED_BRIDGE_HELPERS):
        issues.append(
            "bridge_helpers count drift: "
            f"expected {len(EXPECTED_BRIDGE_HELPERS)}, found {len(bridge_helpers)}"
        )

    for expected in EXPECTED_BRIDGE_HELPERS:
        count = count_exact_entries(string_entries, expected)
        if count == 0:
            issues.append(f"missing bridge_helpers entry: {expected}")
        elif count != 1:
            issues.append(f"duplicate bridge_helpers entry: {expected}:count={count}")

    for index, expected in enumerate(EXPECTED_BRIDGE_HELPERS):
        if index >= len(bridge_helpers):
            continue
        actual = bridge_helpers[index]
        if actual != expected:
            issues.append(
                f"bridge_helpers order drift at index {index}: "
                f"expected {expected!r}, found {actual!r}"
            )

    for entry in string_entries:
        if entry not in EXPECTED_BRIDGE_HELPERS:
            issues.append(f"unexpected bridge_helpers entry: {entry}")
        elif not (repo_root / entry).exists():
            issues.append(f"missing bridge_helpers path: {entry}")

    return issues


def write_sample_root(root: Path) -> None:
    _write(root / MANIFEST_PATH, _sample_manifest())
    for relative_path in EXPECTED_BRIDGE_HELPERS:
        _write(root / relative_path, "present\n")


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(
        prefix="zigux_phase2_bridge_helper_surface_"
    ) as temp_dir:
        root = Path(temp_dir)
        write_sample_root(root)

        issues = validate(root)
        if issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("\n".join(issues))
            return 1
        case_count += 1

        (root / MANIFEST_PATH).unlink()
        issues = validate(root)
        if f"missing manifest file: {MANIFEST_PATH.as_posix()}" not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected missing manifest file was not reported")
            return 1
        case_count += 1

        _write(root / MANIFEST_PATH, "{\n")
        issues = validate(root)
        if not any(issue.startswith("invalid manifest json:") for issue in issues):
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected invalid manifest json was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": []}\n',
        )
        issues = validate(root)
        if "invalid present_surfaces object" not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected invalid present_surfaces object was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"bridge_helpers": "bad"}}\n',
        )
        issues = validate(root)
        if "invalid bridge_helpers list" not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected invalid bridge_helpers list was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            _sample_manifest(list(EXPECTED_BRIDGE_HELPERS[:-1])),
        )
        issues = validate(root)
        missing_issue = (
            "missing bridge_helpers entry: "
            "scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"
        )
        if missing_issue not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected missing bridge_helpers entry was not reported")
            return 1
        case_count += 1

        _write(
            root / MANIFEST_PATH,
            '{"phase": "Phase 2", "present_surfaces": {"bridge_helpers": ['
            '"scripts/zigux/kconfig/conf_bridge.zig", 7, '
            '"scripts/zigux/genksyms.zig", '
            '"scripts/zigux/genksyms_version_before_invalid_long_option_test.zig", '
            '"scripts/zigux/genksyms_version_before_ambiguous_long_option_test.zig"]}}\n',
        )
        issues = validate(root)
        if "invalid bridge_helpers entry at index 1: 7" not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected invalid bridge_helpers entry type was not reported")
            return 1
        case_count += 1

        duplicate_entries = list(EXPECTED_BRIDGE_HELPERS)
        duplicate_entries[-1] = EXPECTED_BRIDGE_HELPERS[-2]
        _write(root / MANIFEST_PATH, _sample_manifest(duplicate_entries))
        issues = validate(root)
        duplicate_issue = (
            "duplicate bridge_helpers entry: "
            "scripts/zigux/genksyms_version_before_invalid_long_option_test.zig:count=2"
        )
        if duplicate_issue not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected duplicate bridge_helpers entry was not reported")
            return 1
        case_count += 1

        reordered_entries = list(EXPECTED_BRIDGE_HELPERS)
        reordered_entries[0], reordered_entries[1] = (
            reordered_entries[1],
            reordered_entries[0],
        )
        _write(root / MANIFEST_PATH, _sample_manifest(reordered_entries))
        issues = validate(root)
        order_issue = (
            "bridge_helpers order drift at index 0: "
            "expected 'scripts/zigux/kconfig/conf_bridge.zig', "
            "found 'scripts/zigux/kconfig/confdata_bridge.zig'"
        )
        if order_issue not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected bridge_helpers order drift was not reported")
            return 1
        case_count += 1

        extra_entries = list(EXPECTED_BRIDGE_HELPERS) + ["scripts/zigux/other.zig"]
        _write(root / MANIFEST_PATH, _sample_manifest(extra_entries))
        _write(root / "scripts/zigux/other.zig", "present\n")
        issues = validate(root)
        if "unexpected bridge_helpers entry: scripts/zigux/other.zig" not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected unexpected bridge_helpers entry was not reported")
            return 1
        case_count += 1

        write_sample_root(root)
        missing_path = root / EXPECTED_BRIDGE_HELPERS[2]
        missing_path.unlink()
        issues = validate(root)
        missing_path_issue = "missing bridge_helpers path: scripts/zigux/genksyms.zig"
        if missing_path_issue not in issues:
            print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=fail")
            print("expected missing bridge_helpers path was not reported")
            return 1
        case_count += 1

    print("PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST=pass")
    print(f"PHASE2_BRIDGE_HELPER_SURFACE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the manifest-backed Phase 2 bridge-helper surface."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("."),
        help="repository root that contains the Phase 2 tool manifest",
    )
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="write a minimal passing sample root to the given directory",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root is not None:
        write_sample_root(args.write_sample_root)
        print(f"wrote sample root to {args.write_sample_root}")
        return 0

    issues = validate(args.root)
    if issues:
        print("PHASE2_BRIDGE_HELPER_SURFACE=fail")
        for issue in issues:
            print(issue)
        return 1

    print("PHASE2_BRIDGE_HELPER_SURFACE=pass")
    print(f"PHASE2_BRIDGE_HELPER_SURFACE_COUNT={len(EXPECTED_BRIDGE_HELPERS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
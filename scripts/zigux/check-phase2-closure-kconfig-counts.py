#!/usr/bin/env python3
"""Fail closed on the Phase 2 closure note's confdata count sentinels."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

PHASE2_CLOSURE_REL = Path("Documentation/zigux/phase2-closure.md")
KCONFIG_CASES_REL = Path("zigux/tests/fixtures/kconfig_bridge/cases.json")
CONFDATA_MANIFEST_REL = Path("zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json")
CONFDATA_BRIDGE_REL = Path("scripts/zigux/kconfig/confdata_bridge.zig")

CASE_COUNT_SENTINEL = "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT"
HELPER_COUNT_SENTINEL = "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT"


def resolve(root: Path, rel: Path) -> Path:
    return root / rel


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise SystemExit(f"required file missing: {path}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def read_json(path: Path) -> object:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid json in required file: {path}: {exc}") from exc


def extract_int_sentinel(issues: list[tuple[str, str]], text: str, key: str) -> int | None:
    matches = re.findall(rf"^\s*[-*]?\s*{re.escape(key)}=(\d+)$", text, flags=re.MULTILINE)
    if not matches:
        issues.append(("MISSING_SENTINEL", key))
        return None
    if len(matches) != 1:
        issues.append(("DUPLICATE_SENTINEL", key))
        return None
    return int(matches[0])


def require_list(issues: list[tuple[str, str]], payload: object, key: str) -> list[object] | None:
    if not isinstance(payload, dict):
        issues.append(("INVALID_JSON_SHAPE", f"{key}:root"))
        return None
    value = payload.get(key)
    if not isinstance(value, list):
        issues.append(("INVALID_JSON_SHAPE", key))
        return None
    return value


def collect_test_names(source_text: str) -> list[str]:
    return re.findall(r'^test "([^"]+)" \{$', source_text, flags=re.MULTILINE)


def collect_issues(root: Path) -> list[tuple[str, str]]:
    issues: list[tuple[str, str]] = []
    closure_text = read_text(resolve(root, PHASE2_CLOSURE_REL))
    cases_payload = read_json(resolve(root, KCONFIG_CASES_REL))
    manifest_payload = read_json(resolve(root, CONFDATA_MANIFEST_REL))
    bridge_text = read_text(resolve(root, CONFDATA_BRIDGE_REL))

    closure_case_count = extract_int_sentinel(issues, closure_text, CASE_COUNT_SENTINEL)
    closure_helper_count = extract_int_sentinel(issues, closure_text, HELPER_COUNT_SENTINEL)

    confdata_cases = require_list(issues, cases_payload, "confdata_cases")
    manifest_cases = require_list(issues, manifest_payload, "cases")
    helper_anchors = require_list(issues, manifest_payload, "helper_local_anchors")

    manifest_case_count = None
    if isinstance(manifest_payload, dict):
        raw_case_count = manifest_payload.get("case_count")
        if not isinstance(raw_case_count, int):
            issues.append(("INVALID_JSON_SHAPE", "case_count"))
        else:
            manifest_case_count = raw_case_count

    if issues:
        return issues

    assert confdata_cases is not None
    assert manifest_cases is not None
    assert helper_anchors is not None
    assert closure_case_count is not None
    assert closure_helper_count is not None
    assert manifest_case_count is not None

    if len(confdata_cases) != manifest_case_count:
        issues.append(
            (
                "CONFDATA_CASE_PACKET_COUNT_MISMATCH",
                f"cases_json={len(confdata_cases)} manifest={manifest_case_count}",
            )
        )

    if len(manifest_cases) != manifest_case_count:
        issues.append(
            (
                "CONFDATA_MANIFEST_CASE_LIST_COUNT_MISMATCH",
                f"manifest_cases={len(manifest_cases)} manifest_case_count={manifest_case_count}",
            )
        )

    if closure_case_count != manifest_case_count:
        issues.append(
            (
                "CLOSURE_CASE_COUNT_MISMATCH",
                f"closure={closure_case_count} manifest={manifest_case_count}",
            )
        )

    if closure_helper_count != len(helper_anchors):
        issues.append(
            (
                "CLOSURE_HELPER_COUNT_MISMATCH",
                f"closure={closure_helper_count} manifest={len(helper_anchors)}",
            )
        )

    source_tests = collect_test_names(bridge_text)
    for anchor in helper_anchors:
        if not isinstance(anchor, str):
            issues.append(("INVALID_JSON_SHAPE", "helper_local_anchors:item"))
            continue
        count = source_tests.count(anchor)
        if count == 0:
            issues.append(("MISSING_HELPER_ANCHOR_TEST", anchor))
        elif count != 1:
            issues.append(("DUPLICATE_HELPER_ANCHOR_TEST", f"{anchor}:count={count}"))

    return issues


def emit_issues(issues: list[tuple[str, str]]) -> int:
    grouped: dict[str, list[str]] = {}
    for code, value in issues:
        grouped.setdefault(code, []).append(value)

    print("PHASE2_CLOSURE_KCONFIG_COUNTS=fail")
    for code, values in grouped.items():
        print(f"{code}_START")
        for value in values:
            print(value)
        print(f"{code}_END")
    return 1


def build_sample_root(root: Path) -> None:
    closure_text = """# Phase 2 Closure

- PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=3
- PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=4
"""
    cases_payload = {
        "conf_cases": [],
        "confdata_cases": [
            {"name": "sample", "input": "sample.config", "expected": "sample_expected.json"},
            {"name": "escaped_strings", "input": "escaped_strings.config", "expected": "escaped_strings_expected.json"},
            {"name": "duplicate_assignments", "input": "duplicate_assignments.config", "expected": "duplicate_assignments_expected.json"},
        ],
    }
    manifest_payload = {
        "tool": "scripts/zigux/kconfig/confdata_bridge.zig",
        "status": "closed",
        "mode": "bounded config bridge",
        "fixture_root": "zigux/tests/fixtures/kconfig_bridge",
        "fixture_case_source": "zigux/tests/fixtures/kconfig_bridge/cases.json",
        "case_count": 3,
        "cases": [
            "sample",
            "escaped_strings",
            "duplicate_assignments",
        ],
        "helper_local_anchors": [
            "confdata bridge parses bounded config states",
            "confdata bridge emits bounded json output",
            "confdata bridge keeps only the last assignment for duplicate symbols",
            "confdata bridge preserves duplicate unset ownership on allocation failure",
        ],
    }
    bridge_text = """const std = @import("std");

test "confdata bridge parses bounded config states" {
    try std.testing.expect(true);
}

test "confdata bridge emits bounded json output" {
    try std.testing.expect(true);
}

test "confdata bridge keeps only the last assignment for duplicate symbols" {
    try std.testing.expect(true);
}

test "confdata bridge preserves duplicate unset ownership on allocation failure" {
    try std.testing.expect(true);
}
"""

    write_text(resolve(root, PHASE2_CLOSURE_REL), closure_text)
    write_text(resolve(root, KCONFIG_CASES_REL), json.dumps(cases_payload, indent=2) + "\n")
    write_text(resolve(root, CONFDATA_MANIFEST_REL), json.dumps(manifest_payload, indent=2) + "\n")
    write_text(resolve(root, CONFDATA_BRIDGE_REL), bridge_text)


def run_self_test() -> int:
    checks_run = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase2_closure_kconfig_counts_") as tmp_dir:
        root = Path(tmp_dir)

        build_sample_root(root)
        assert collect_issues(root) == []
        checks_run += 1

        build_sample_root(root)
        closure_path = resolve(root, PHASE2_CLOSURE_REL)
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=3",
                "PHASE2_KCONFIG_BRIDGE_CONFDATA_CASE_COUNT=4",
                1,
            ),
            encoding="utf-8",
        )
        assert ("CLOSURE_CASE_COUNT_MISMATCH", "closure=4 manifest=3") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        closure_path = resolve(root, PHASE2_CLOSURE_REL)
        closure_path.write_text(
            closure_path.read_text(encoding="utf-8").replace(
                "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=4",
                "PHASE2_KCONFIG_BRIDGE_CONFDATA_HELPER_ANCHOR_COUNT=2",
                1,
            ),
            encoding="utf-8",
        )
        assert ("CLOSURE_HELPER_COUNT_MISMATCH", "closure=2 manifest=4") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        manifest_path = resolve(root, CONFDATA_MANIFEST_REL)
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        payload["case_count"] = 5
        manifest_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("CONFDATA_CASE_PACKET_COUNT_MISMATCH", "cases_json=3 manifest=5") in issues
        assert ("CLOSURE_CASE_COUNT_MISMATCH", "closure=3 manifest=5") in issues
        checks_run += 1

        build_sample_root(root)
        bridge_path = resolve(root, CONFDATA_BRIDGE_REL)
        bridge_path.write_text(
            bridge_path.read_text(encoding="utf-8").replace(
                'test "confdata bridge emits bounded json output" {\n    try std.testing.expect(true);\n}\n\n',
                "",
                1,
            ),
            encoding="utf-8",
        )
        assert ("MISSING_HELPER_ANCHOR_TEST", "confdata bridge emits bounded json output") in collect_issues(root)
        checks_run += 1

        build_sample_root(root)
        closure_path = resolve(root, PHASE2_CLOSURE_REL)
        closure_path.write_text("# Phase 2 Closure\n", encoding="utf-8")
        issues = collect_issues(root)
        assert ("MISSING_SENTINEL", CASE_COUNT_SENTINEL) in issues
        assert ("MISSING_SENTINEL", HELPER_COUNT_SENTINEL) in issues
        checks_run += 1

    print("PHASE2_CLOSURE_KCONFIG_COUNTS_SELF_TEST=pass")
    print(f"PHASE2_CLOSURE_KCONFIG_COUNTS_SELF_TEST_CASE_COUNT={checks_run}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail closed on the Phase 2 closure note's confdata count sentinels."
    )
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="Repository root to inspect")
    parser.add_argument(
        "--write-sample-root",
        type=Path,
        help="Write a minimal passing sample root to the given directory and exit",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in contract checks")
    args = parser.parse_args()

    if args.write_sample_root is not None:
        build_sample_root(args.write_sample_root.resolve())
        print(f"PHASE2_CLOSURE_KCONFIG_COUNTS_SAMPLE_ROOT={args.write_sample_root.resolve()}")
        return 0

    if args.self_test:
        return run_self_test()

    issues = collect_issues(args.root.resolve())
    if issues:
        return emit_issues(issues)

    manifest = read_json(resolve(args.root.resolve(), CONFDATA_MANIFEST_REL))
    assert isinstance(manifest, dict)
    helper_anchors = manifest["helper_local_anchors"]
    assert isinstance(helper_anchors, list)
    print("PHASE2_CLOSURE_KCONFIG_COUNTS=pass")
    print(f"PHASE2_CLOSURE_KCONFIG_COUNTS_CONFDATA_CASE_COUNT={manifest['case_count']}")
    print(f"PHASE2_CLOSURE_KCONFIG_COUNTS_CONFDATA_HELPER_ANCHOR_COUNT={len(helper_anchors)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FILES = [
    "Documentation/zigux/phase1-closure.md",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/phase1_helpers.zig",
    "tools/lib/rbtree.zig",
    "tools/lib/string.zig",
]

RBTREE_HELPER_ANCHORS = [
    'test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"',
    'test "rbtree findAdd keeps the first duplicate and inserts new keys"',
    'test "rbtree nextMatch walks the duplicate range in order"',
]

RBTREE_FIXTURE_KEYS = [
    "find_found_key",
    "find_missing",
    "find_first_serial",
    "next_match_serials",
    "next_match_terminal_null",
]

STRING_HELPER_ANCHORS = [
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    'test "phase 1 string replaceChar stops at embedded NUL"',
]


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def count_marker(text: str, label: str, marker: str, expected_count: int = 1) -> list[str]:
    actual_count = text.count(marker)
    if actual_count == expected_count:
        return []
    return [f"{label}:expected={expected_count}:actual={actual_count}:{marker}"]


def collect_phase1_closure_issues(root: Path) -> list[str]:
    text = (root / "Documentation/zigux/phase1-closure.md").read_text(encoding="utf-8")
    issues: list[str] = []
    for marker in RBTREE_HELPER_ANCHORS[:1] + STRING_HELPER_ANCHORS[:1]:
        issues.extend(count_marker(text, "phase1_closure_anchor", marker))
    for key in RBTREE_FIXTURE_KEYS:
        issues.extend(count_marker(text, "phase1_closure_key", key))
    return issues


def collect_manifest_issues(root: Path) -> list[str]:
    manifest = json.loads(
        (root / "zigux/tests/fixtures/phase1_helper_manifest.json").read_text(encoding="utf-8")
    )
    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["phase1_manifest:review_anchors_missing"]

    issues: list[str] = []

    rbtree = review_anchors.get("tools/lib/rbtree.zig")
    if not isinstance(rbtree, dict):
        issues.append("phase1_manifest:rbtree_review_anchors_missing")
    else:
        helper_anchors = rbtree.get("helper_test_anchors")
        fixture_keys = rbtree.get("parity_fixture_keys")
        if helper_anchors != list(helper_anchors or []):
            issues.append("phase1_manifest:rbtree_helper_test_anchors_not_list")
        if fixture_keys != list(fixture_keys or []):
            issues.append("phase1_manifest:rbtree_parity_fixture_keys_not_list")
        if isinstance(helper_anchors, list):
            for marker in RBTREE_HELPER_ANCHORS:
                if helper_anchors.count(marker) != 1:
                    issues.append(f"phase1_manifest:rbtree_helper_anchor:{marker}:count={helper_anchors.count(marker)}")
        if isinstance(fixture_keys, list):
            for key in RBTREE_FIXTURE_KEYS:
                if fixture_keys.count(key) != 1:
                    issues.append(f"phase1_manifest:rbtree_fixture_key:{key}:count={fixture_keys.count(key)}")

    string = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string, dict):
        issues.append("phase1_manifest:string_review_anchors_missing")
    else:
        helper_anchors = string.get("helper_test_anchors")
        if helper_anchors != list(helper_anchors or []):
            issues.append("phase1_manifest:string_helper_test_anchors_not_list")
        if isinstance(helper_anchors, list):
            for marker in STRING_HELPER_ANCHORS:
                if helper_anchors.count(marker) != 1:
                    issues.append(f"phase1_manifest:string_helper_anchor:{marker}:count={helper_anchors.count(marker)}")

    return issues


def collect_phase1_helpers_issues(root: Path) -> list[str]:
    text = (root / "zigux/tests/phase1_helpers.zig").read_text(encoding="utf-8")
    issues: list[str] = []
    for marker in STRING_HELPER_ANCHORS:
        issues.extend(count_marker(text, "phase1_helpers_anchor", marker))
    for key in RBTREE_FIXTURE_KEYS:
        issues.extend(count_marker(text, "phase1_helpers_fixture", f"fixture.rbtree.{key}"))
    return issues


def collect_helper_source_issues(root: Path) -> list[str]:
    rbtree_text = (root / "tools/lib/rbtree.zig").read_text(encoding="utf-8")
    string_text = (root / "tools/lib/string.zig").read_text(encoding="utf-8")

    issues: list[str] = []
    for marker in RBTREE_HELPER_ANCHORS:
        issues.extend(count_marker(rbtree_text, "rbtree_source_anchor", marker))
    for marker in STRING_HELPER_ANCHORS[:1]:
        issues.extend(count_marker(string_text, "string_source_anchor", marker))
    return issues


def validate_root(root: Path) -> list[str]:
    missing_files = collect_missing_files(root)
    if missing_files:
        return [f"missing_file:{rel}" for rel in missing_files]

    issues: list[str] = []
    issues.extend(collect_phase1_closure_issues(root))
    issues.extend(collect_manifest_issues(root))
    issues.extend(collect_phase1_helpers_issues(root))
    issues.extend(collect_helper_source_issues(root))
    return issues


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_self_test_root(root: Path) -> None:
    write_text(
        root / "Documentation/zigux/phase1-closure.md",
        "\n".join(
            [
                RBTREE_HELPER_ANCHORS[0],
                STRING_HELPER_ANCHORS[0],
                *RBTREE_FIXTURE_KEYS,
            ]
        )
        + "\n",
    )
    write_text(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/rbtree.zig": {
                        "helper_test_anchors": RBTREE_HELPER_ANCHORS,
                        "parity_fixture_keys": RBTREE_FIXTURE_KEYS,
                    },
                    "tools/lib/string.zig": {
                        "helper_test_anchors": STRING_HELPER_ANCHORS,
                    },
                }
            },
            indent=2,
        )
        + "\n",
    )
    write_text(
        root / "zigux/tests/phase1_helpers.zig",
        "\n".join(
            STRING_HELPER_ANCHORS
            + [f"fixture.rbtree.{key}" for key in RBTREE_FIXTURE_KEYS]
        )
        + "\n",
    )
    write_text(root / "tools/lib/rbtree.zig", "\n".join(RBTREE_HELPER_ANCHORS) + "\n")
    write_text(root / "tools/lib/string.zig", STRING_HELPER_ANCHORS[0] + "\n")



def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1_rbtree_string_review_") as tmp_dir:
        root = Path(tmp_dir)
        build_self_test_root(root)
        assert validate_root(root) == []

        write_text(root / "Documentation/zigux/phase1-closure.md", "")
        issues = validate_root(root)
        assert (
            'phase1_closure_anchor:expected=1:actual=0:test "rbtree replaceNodeCached keeps non-leftmost leftmost unchanged"'
            in issues
        )

        build_self_test_root(root)
        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["helper_test_anchors"].pop()
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = validate_root(root)
        assert (
            'phase1_manifest:rbtree_helper_anchor:test "rbtree nextMatch walks the duplicate range in order":count=0'
            in issues
        )

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/rbtree.zig"]["parity_fixture_keys"].remove("find_missing")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = validate_root(root)
        assert "phase1_manifest:rbtree_fixture_key:find_missing:count=0" in issues

        build_self_test_root(root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["helper_test_anchors"] = [
            STRING_HELPER_ANCHORS[1]
        ]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        issues = validate_root(root)
        assert (
            'phase1_manifest:string_helper_anchor:test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace":count=0'
            in issues
        )

        build_self_test_root(root)
        write_text(root / "zigux/tests/phase1_helpers.zig", STRING_HELPER_ANCHORS[0] + "\n")
        issues = validate_root(root)
        assert "phase1_helpers_fixture:expected=1:actual=0:fixture.rbtree.find_found_key" in issues

        build_self_test_root(root)
        write_text(root / "tools/lib/rbtree.zig", RBTREE_HELPER_ANCHORS[0] + "\n")
        issues = validate_root(root)
        assert (
            'rbtree_source_anchor:expected=1:actual=0:test "rbtree findAdd keeps the first duplicate and inserts new keys"'
            in issues
        )

        build_self_test_root(root)
        write_text(root / "tools/lib/string.zig", "")
        issues = validate_root(root)
        assert (
            'string_source_anchor:expected=1:actual=0:test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"'
            in issues
        )

        build_self_test_root(root)
        (root / "tools/lib/string.zig").unlink()
        issues = validate_root(root)
        assert "missing_file:tools/lib/string.zig" in issues

    print("PHASE1_RBTREE_STRING_REVIEW_ANCHORS_SELF_TEST=pass")
    print("PHASE1_RBTREE_STRING_REVIEW_ANCHORS_SELF_TEST_CASE_COUNT=8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check the shipped Phase 1 rbtree and string review-anchor packet stays aligned."
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in checker coverage without reading a repo checkout.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Alternate Zigux tree root to validate.",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = validate_root(args.root.resolve())
    if issues:
        print("PHASE1_RBTREE_STRING_REVIEW_ANCHORS=fail")
        print("PHASE1_RBTREE_STRING_REVIEW_ANCHORS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_RBTREE_STRING_REVIEW_ANCHORS_ISSUES_END")
        return 1

    print("PHASE1_RBTREE_STRING_REVIEW_ANCHORS=pass")
    print(
        "PHASE1_RBTREE_STRING_REVIEW_ANCHORS_MARKER_COUNT="
        f"{2 + len(RBTREE_FIXTURE_KEYS) + len(RBTREE_HELPER_ANCHORS) + len(RBTREE_FIXTURE_KEYS) + len(STRING_HELPER_ANCHORS) + len(RBTREE_HELPER_ANCHORS) + 1}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path


SELF_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else SELF_PATH.parent

TARGET = Path("tools/lib/string.zig")
MANIFEST = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FUNCTION_MARKERS = [
    "pub fn strHasPrefix(str: []const u8, prefix: []const u8) usize {",
    "pub fn strHasSuffix(str: []const u8, suffix: []const u8) usize {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn memparse(text: []const u8) MemparseResult {",
    "pub fn kbasename(path: []const u8) []const u8 {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnlen(buf: []const u8, count: usize) usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
]

REQUIRED_TEST_MARKERS = [
    'test "strHasPrefix returns the matched prefix length with C-string semantics" {',
    'test "strHasSuffix returns the matched suffix length with C-string semantics" {',
    'test "strstarts mirrors the header-level prefix helper" {',
    'test "strEndsWith honors C-string boundaries" {',
    'test "sysfsStreq treats trailing newline and NUL as equivalent" {',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence" {',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order" {',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists" {',
    'test "matchString finds C-string matches and preserves first-match order" {',
    'test "match_string mirrors matchString for empty and matched lists" {',
    'test "memparse handles decimal hexadecimal octal and suffixes" {',
    'test "memparse keeps original rest when sign is not followed by digits" {',
    'test "memparse saturates signed overflow instead of trapping" {',
    'test "memparse clamps explicit positive signed overflow" {',
    'test "memparse keeps signed values and their trailing rest aligned" {',
    'test "memparse consumes suffix after saturation" {',
    'test "memparse applies suffixes before signed clamping" {',
    'test "kbasename returns the final path component with C-string semantics" {',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace" {',
    'test "memchrInv follows the earliest dirty byte as long buffers change" {',
    'test "strchr mirrors full-length C-string searches" {',
    'test "strrchr finds the last in-range match with C-string semantics" {',
    'test "strpbrk finds the first accepted byte with C-string semantics" {',
    'test "strnchr honors count and C-string boundaries" {',
    'test "strnlen honors count and C-string boundaries" {',
    'test "strnchrNul returns the first match, NUL, or count boundary" {',
]

EXPECTED_MANIFEST = {
    "helpers": {
        "review_anchors.tools/lib/string.zig": {
            "memparse_review_anchors": [
                'test "memparse handles decimal hexadecimal octal and suffixes" {',
                'test "memparse keeps original rest when sign is not followed by digits" {',
                'test "memparse saturates signed overflow instead of trapping" {',
                'test "memparse clamps explicit positive signed overflow" {',
                'test "memparse keeps signed values and their trailing rest aligned" {',
                'test "memparse consumes suffix after saturation" {',
                'test "memparse applies suffixes before signed clamping" {',
            ],
            "prefix_suffix_review_anchors": [
                'test "strHasPrefix returns the matched prefix length with C-string semantics" {',
                'test "strHasSuffix returns the matched suffix length with C-string semantics" {',
                'test "strstarts mirrors the header-level prefix helper" {',
                'test "strEndsWith honors C-string boundaries" {',
            ],
            "sysfs_review_anchors": [
                'test "sysfsStreq treats trailing newline and NUL as equivalent" {',
                'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence" {',
                'test "sysfsMatchString finds newline-aware matches and preserves first-match order" {',
                'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists" {',
            ],
            "lookup_review_anchors": [
                'test "matchString finds C-string matches and preserves first-match order" {',
                'test "match_string mirrors matchString for empty and matched lists" {',
            ],
            "counted_search_review_anchors": [
                'test "strchr mirrors full-length C-string searches" {',
                'test "strrchr finds the last in-range match with C-string semantics" {',
                'test "strpbrk finds the first accepted byte with C-string semantics" {',
                'test "strnchr honors count and C-string boundaries" {',
                'test "strnlen honors count and C-string boundaries" {',
                'test "strnchrNul returns the first match, NUL, or count boundary" {',
            ],
            "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace" {',
            "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change" {',
            "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics" {',
            "next_safe_step_note": "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.",
        }
    },
    "lane_helpers": [
        "tools/lib/string.zig",
    ],
}


def repo_root(explicit_root: str | None) -> Path:
    return Path(explicit_root).resolve() if explicit_root else DEFAULT_ROOT


def read_text(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def read_json(root: Path, rel: Path) -> object:
    return json.loads(read_text(root, rel))


def nested_get(payload: object, dotted_path: str) -> object:
    current = payload
    for key in dotted_path.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def collect_issues(root: Path) -> list[str]:
    issues: list[str] = []

    target_path = root / TARGET
    if not target_path.exists():
        return [f"missing_file:{TARGET.as_posix()}"]

    manifest_path = root / MANIFEST
    if not manifest_path.exists():
        return [f"missing_file:{MANIFEST.as_posix()}"]

    text = read_text(root, TARGET)
    manifest = read_json(root, MANIFEST)

    for marker in REQUIRED_FUNCTION_MARKERS:
        if marker not in text:
            issues.append(f"function:{marker}")

    for marker in REQUIRED_TEST_MARKERS:
        if marker not in text:
            issues.append(f"test:{marker}")

    helpers = nested_get(manifest, "helpers")
    if not isinstance(helpers, list) or "tools/lib/string.zig" not in helpers:
        issues.append("manifest:helpers=tools/lib/string.zig")

    direct_helpers = nested_get(manifest, "lane_sequencing.direct_anchor_followup_helpers")
    if not isinstance(direct_helpers, list) or EXPECTED_MANIFEST["lane_helpers"][0] not in direct_helpers:
        issues.append("manifest:direct_anchor_followup_helpers=tools/lib/string.zig")

    review_anchors = nested_get(manifest, "review_anchors")
    string_review_anchors = (
        review_anchors.get("tools/lib/string.zig")
        if isinstance(review_anchors, dict)
        else None
    )
    if not isinstance(string_review_anchors, dict):
        issues.append("manifest:review_anchors.tools/lib/string.zig")
        return issues

    for dotted_path, expected_value in EXPECTED_MANIFEST["helpers"]["review_anchors.tools/lib/string.zig"].items():
        manifest_value = string_review_anchors.get(dotted_path)
        if manifest_value != expected_value:
            issues.append(f"manifest:{dotted_path}")

    return issues


def fixture_manifest() -> dict[str, object]:
    return {
        "phase": "Phase 1",
        "status": "closed",
        "helper_count": 13,
        "helpers": [
            "tools/lib/argv_split.zig",
            "tools/lib/bitmap.zig",
            "tools/lib/cmdline.zig",
            "tools/lib/ctype.zig",
            "tools/lib/find_bit.zig",
            "tools/lib/hweight.zig",
            "tools/lib/list_sort.zig",
            "tools/lib/rbtree.zig",
            "tools/lib/slab.zig",
            "tools/lib/str_error_r.zig",
            "tools/lib/string.zig",
            "tools/lib/vsprintf.zig",
            "tools/lib/zalloc.zig",
        ],
        "lane_sequencing": {
            "shared_replay_parked_helpers": [
                "tools/lib/argv_split.zig",
                "tools/lib/cmdline.zig",
                "tools/lib/ctype.zig",
                "tools/lib/hweight.zig",
                "tools/lib/list_sort.zig",
                "tools/lib/slab.zig",
                "tools/lib/str_error_r.zig",
                "tools/lib/vsprintf.zig",
                "tools/lib/zalloc.zig",
            ],
            "direct_anchor_followup_helpers": [
                "tools/lib/bitmap.zig",
                "tools/lib/find_bit.zig",
                "tools/lib/rbtree.zig",
                "tools/lib/string.zig",
            ],
        },
        "review_anchors": {
            "tools/lib/string.zig": copy.deepcopy(
                EXPECTED_MANIFEST["helpers"]["review_anchors.tools/lib/string.zig"]
            ),
        },
    }


def fixture_string() -> str:
    lines: list[str] = []
    lines.extend(REQUIRED_FUNCTION_MARKERS)
    lines.append("")
    lines.extend(REQUIRED_TEST_MARKERS)
    lines.append("")
    return "\n".join(lines) + "\n"


def build_fixture(root: Path) -> None:
    (root / TARGET.parent).mkdir(parents=True, exist_ok=True)
    (root / MANIFEST.parent).mkdir(parents=True, exist_ok=True)
    (root / TARGET).write_text(fixture_string(), encoding="utf-8")
    (root / MANIFEST).write_text(json.dumps(fixture_manifest(), indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_review_anchors_") as tmp_dir:
        root = Path(tmp_dir)

        if collect_issues(root) != [f"missing_file:{TARGET.as_posix()}"]:
            raise SystemExit("phase1-string-review:self-test:missing_target")
        cases += 1

        build_fixture(root)
        if collect_issues(root):
            raise SystemExit("phase1-string-review:self-test:baseline")

        text = read_text(root, TARGET)
        (root / TARGET).write_text(
            text.replace(REQUIRED_TEST_MARKERS[10] + "\n", "", 1),
            encoding="utf-8",
        )
        if f"test:{REQUIRED_TEST_MARKERS[10]}" not in collect_issues(root):
            raise SystemExit("phase1-string-review:self-test:missing_test")
        cases += 1

        build_fixture(root)
        text = read_text(root, TARGET)
        (root / TARGET).write_text(
            text.replace(REQUIRED_FUNCTION_MARKERS[2] + "\n", "", 1),
            encoding="utf-8",
        )
        if f"function:{REQUIRED_FUNCTION_MARKERS[2]}" not in collect_issues(root):
            raise SystemExit("phase1-string-review:self-test:missing_function")
        cases += 1

        build_fixture(root)
        manifest = fixture_manifest()
        anchors = manifest["review_anchors"]["tools/lib/string.zig"]
        anchors["sysfs_review_anchors"] = anchors["sysfs_review_anchors"][:-1]
        (root / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if "manifest:sysfs_review_anchors" not in collect_issues(root):
            raise SystemExit("phase1-string-review:self-test:missing_manifest_anchor_group")
        cases += 1

        build_fixture(root)
        manifest = fixture_manifest()
        manifest["lane_sequencing"]["direct_anchor_followup_helpers"] = [
            "tools/lib/bitmap.zig",
            "tools/lib/find_bit.zig",
            "tools/lib/rbtree.zig",
        ]
        (root / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if "manifest:direct_anchor_followup_helpers=tools/lib/string.zig" not in collect_issues(root):
            raise SystemExit("phase1-string-review:self-test:missing_lane_helper")
        cases += 1

    print("PHASE1_STRING_REVIEW_ANCHORS_SELF_TEST=pass")
    print(f"PHASE1_STRING_REVIEW_ANCHORS_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the current Phase 1 string direct-review anchors."
    )
    parser.add_argument("--self-test", action="store_true", help="Run embedded checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux root.")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    issues = collect_issues(repo_root(args.root))
    if issues:
        print("PHASE1_STRING_REVIEW_ANCHORS=fail")
        print("PHASE1_STRING_REVIEW_ANCHORS_ISSUES_START")
        for issue in issues:
            print(issue)
        print("PHASE1_STRING_REVIEW_ANCHORS_ISSUES_END")
        return 1

    print("PHASE1_STRING_REVIEW_ANCHORS=pass")
    print(f"PHASE1_STRING_REVIEW_ANCHORS_FUNCTION_MARKER_COUNT={len(REQUIRED_FUNCTION_MARKERS)}")
    print(f"PHASE1_STRING_REVIEW_ANCHORS_TEST_MARKER_COUNT={len(REQUIRED_TEST_MARKERS)}")
    print("PHASE1_STRING_REVIEW_ANCHORS_MANIFEST_GROUP_COUNT=9")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

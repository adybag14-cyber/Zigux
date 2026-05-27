#!/usr/bin/env python3
"""Guard the current Phase 1 string memparse review-rule packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_REVIEW_PACKET_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
STRING_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    STRING_HELPER_REL,
    STRING_REVIEW_PACKET_REL,
    STRING_LANE_NOTE_REL,
    MANIFEST_REL,
)

HELPER_SOURCE_MARKER = "pub fn memparse(text: []const u8) MemparseResult {"
HELPER_TEST_ANCHORS = (
    'test "memparse handles decimal hexadecimal octal and suffixes"',
    'test "memparse keeps original rest when sign is not followed by digits"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "memparse clamps explicit positive signed overflow"',
    'test "memparse keeps signed values and their trailing rest aligned"',
    'test "memparse consumes suffix after saturation"',
    'test "memparse applies suffixes before signed clamping"',
)
REVIEW_PACKET_ANCHORS = (
    '"memparse_review_anchors": [',
    '        \'test "memparse handles decimal hexadecimal octal and suffixes"\'',
    '        \'test "memparse keeps original rest when sign is not followed by digits"\'',
    '        \'test "memparse saturates signed overflow instead of trapping"\'',
    '        \'test "memparse clamps explicit positive signed overflow"\'',
    '        \'test "memparse keeps signed values and their trailing rest aligned"\'',
    '        \'test "memparse consumes suffix after saturation"\'',
    '        \'test "memparse applies suffixes before signed clamping"\'',
    '"memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation"',
)
LANE_NOTE_MARKERS = (
    "`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
)
EXPECTED_MANIFEST_ANCHORS = list(HELPER_TEST_ANCHORS)
EXPECTED_MANIFEST_SUMMARY = (
    "helper-local memparse safety anchors stay explicit through the direct string tests so "
    "sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split "
    "aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of "
    "trapping, and suffixes are still consumed after saturation"
)


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def collect_duplicate_json_key_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(collect_duplicate_json_key_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for item in data:
            paths.extend(collect_duplicate_json_key_paths(item, prefix))
    return paths


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures = [f"missing_file:{path.as_posix()}" for path in REQUIRED_FILES if not (root / path).is_file()]
    if failures:
        return failures

    helper_text = read_text(root, STRING_HELPER_REL)
    review_text = read_text(root, STRING_REVIEW_PACKET_REL)
    lane_text = read_text(root, STRING_LANE_NOTE_REL)

    failures.extend(require_exact_occurrence(helper_text, "helper:source", HELPER_SOURCE_MARKER))
    for anchor in HELPER_TEST_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper:{anchor}", anchor))
    for anchor in REVIEW_PACKET_ANCHORS:
        failures.extend(require_exact_occurrence(review_text, f"review:{anchor}", anchor))
    for marker in LANE_NOTE_MARKERS:
        failures.extend(require_exact_occurrence(lane_text, f"lane:{marker}", marker))

    manifest_text = read_text(root, MANIFEST_REL)
    try:
        manifest = load_json_with_duplicate_tracking(manifest_text)
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    duplicate_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_paths]

    failures.extend(
        require_exact_value(
            "manifest:review_anchors.tools/lib/string.zig.memparse_review_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "memparse_review_anchors")),
            EXPECTED_MANIFEST_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:review_anchors.tools/lib/string.zig.memparse_review_summary",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "memparse_review_summary")),
            EXPECTED_MANIFEST_SUMMARY,
        )
    )

    return failures


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/string.zig": {
                        "memparse_review_anchors": list(EXPECTED_MANIFEST_ANCHORS),
                        "memparse_review_summary": EXPECTED_MANIFEST_SUMMARY,
                    }
                }
            },
            indent=2,
        )
        + "\n"
    )


def write_sample_root(root: Path) -> None:
    write_text(root / STRING_HELPER_REL, "\n".join((HELPER_SOURCE_MARKER, *HELPER_TEST_ANCHORS)) + "\n")
    write_text(root / STRING_REVIEW_PACKET_REL, "\n".join(REVIEW_PACKET_ANCHORS) + "\n")
    write_text(root / STRING_LANE_NOTE_REL, "\n".join(LANE_NOTE_MARKERS) + "\n")
    write_text(root / MANIFEST_REL, make_sample_manifest())


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase1-string-memparse-review-rule-") as tmp_dir:
        root = Path(tmp_dir)

        if "missing_file:tools/lib/string.zig" not in collect_failures(root):
            print("phase1-string-memparse-review-rule:self-test:missing_file")
            return 1

        write_sample_root(root)
        if collect_failures(root):
            print("phase1-string-memparse-review-rule:self-test:baseline")
            return 1

        helper_path = root / STRING_HELPER_REL
        helper_path.write_text(helper_path.read_text(encoding="utf-8").replace(HELPER_TEST_ANCHORS[0] + "\n", "", 1), encoding="utf-8")
        if not any(item.startswith(f"helper:{HELPER_TEST_ANCHORS[0]}:expected=1:actual=0") for item in collect_failures(root)):
            print("phase1-string-memparse-review-rule:self-test:helper_anchor")
            return 1

        write_sample_root(root)
        review_path = root / STRING_REVIEW_PACKET_REL
        review_path.write_text(review_path.read_text(encoding="utf-8").replace(REVIEW_PACKET_ANCHORS[-1] + "\n", "", 1), encoding="utf-8")
        if not any(item.startswith(f"review:{REVIEW_PACKET_ANCHORS[-1]}:expected=1:actual=0") for item in collect_failures(root)):
            print("phase1-string-memparse-review-rule:self-test:review_summary")
            return 1

        write_sample_root(root)
        lane_path = root / STRING_LANE_NOTE_REL
        lane_path.write_text(lane_path.read_text(encoding="utf-8").replace(LANE_NOTE_MARKERS[1] + "\n", "", 1), encoding="utf-8")
        if not any(item.startswith(f"lane:{LANE_NOTE_MARKERS[1]}:expected=1:actual=0") for item in collect_failures(root)):
            print("phase1-string-memparse-review-rule:self-test:lane_marker")
            return 1

        write_sample_root(root)
        manifest_path = root / MANIFEST_REL
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["memparse_review_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any(item.startswith("manifest:review_anchors.tools/lib/string.zig.memparse_review_summary:expected=") for item in collect_failures(root)):
            print("phase1-string-memparse-review-rule:self-test:manifest_summary")
            return 1

        write_sample_root(root)
        manifest_path.write_text("{\n", encoding="utf-8")
        if "manifest:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1" not in collect_failures(root):
            print("phase1-string-memparse-review-rule:self-test:manifest_invalid_json")
            return 1

        write_sample_root(root)
        text = manifest_path.read_text(encoding="utf-8")
        needle = '      "memparse_review_anchors": ['
        manifest_path.write_text(text.replace(needle, '      "memparse_review_anchors": [],\n' + needle, 1), encoding="utf-8")
        if "manifest:duplicate_json_key:review_anchors.tools/lib/string.zig.memparse_review_anchors" not in collect_failures(root):
            print("phase1-string-memparse-review-rule:self-test:manifest_duplicate_key")
            return 1

    print("PHASE1_STRING_MEMPARSE_REVIEW_RULE_SELF_TEST=pass")
    print("PHASE1_STRING_MEMPARSE_REVIEW_RULE_SELF_TEST_CASE_COUNT=6")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run self-tests")
    parser.add_argument("--write-sample-root", help="write a current-like sample root")
    args = parser.parse_args()

    if args.write_sample_root:
        write_sample_root(Path(args.write_sample_root).resolve())
        print("PHASE1_STRING_MEMPARSE_REVIEW_RULE_SAMPLE_ROOT=written")
        return 0

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_STRING_MEMPARSE_REVIEW_RULE=fail")
        for failure in failures:
            print(failure)
        return 1

    print("phase1-string-memparse-review-rule:ok")
    print(f"PHASE1_STRING_MEMPARSE_REVIEW_RULE_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_STRING_MEMPARSE_REVIEW_RULE_REQUIRED_MARKER_COUNT="
        f"{1 + len(HELPER_TEST_ANCHORS) + len(REVIEW_PACKET_ANCHORS) + len(LANE_NOTE_MARKERS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

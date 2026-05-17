#!/usr/bin/env python3
"""Guard the Phase 1 string review packet against live helper, manifest, and lane-note drift."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[2]
STRING_HELPER_REL = Path("tools/lib/string.zig")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

STRING_REVIEW_RULE_LINE = (
    "- the still-open string sysfs follow-through, if it reopens, should stay on one "
    "string-only shared review-rule packet across "
    "`zigux/tests/fixtures/phase1_helper_manifest.json`, "
    "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and "
    "`scripts/zigux/check-phase1-string-review-packet.py`; treat the older "
    "`Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` "
    "names as historical packet members until current `master` exposes them again"
)

EXPECTED_STRING_ANCHORS = {
    "helper_test_anchors": [
        'test "strtobool accepts common Linux forms"',
        'test "strlcpy copies and returns the source length"',
        'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
        'test "strscpyPad zero-pads the tail after a short source"',
        'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
        'test "strscpyPad preserves strscpy truncation semantics"',
        'test "strscpy_pad mirrors strscpyPad padding semantics"',
        'test "streq matches C-string equality semantics"',
        'test "skip trim remove and replace spaces work in place"',
        'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        'test "strreplace mirrors replaceChar C-string semantics"',
        'test "strHasPrefix returns the matched prefix length with C-string semantics"',
        'test "strstarts mirrors the header-level prefix helper"',
        'test "strEndsWith honors C-string boundaries"',
        'test "kbasename returns the final path component with C-string semantics"',
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
        'test "matchString finds C-string matches and preserves first-match order"',
        'test "match_string mirrors matchString for empty and matched lists"',
        'test "memdup and memchrInv preserve byte content"',
        'test "memchr_inv mirrors memchrInv byte-search semantics"',
        'test "memchrInv keeps long-buffer first-dirty-byte results stable"',
        'test "memchrInv follows the earliest dirty byte as long buffers change"',
        'test "memchrInv dirty-word shortcut handles zero-value scans at word boundaries"',
        'test "memchrInv zero-value scans keep the earliest dirty byte across every prefix alignment"',
        'test "memchrInv keeps the earliest dirty byte for long non-zero scans across alignments"',
        'test "memchrInv keeps the earliest dirty byte for long zero-value scans across alignments"',
        'test "memchrInv short zero-value scans stay byte-accurate"',
        'test "memchrInv keeps the earliest dirty byte across the fast-path cutoff"',
        'test "memparse handles decimal hexadecimal octal and suffixes"',
        'test "memparse keeps original rest when sign is not followed by digits"',
        'test "memparse saturates signed overflow instead of trapping"',
        'test "memparse clamps explicit positive signed overflow"',
        'test "memparse keeps signed values and their trailing rest aligned"',
        'test "memparse consumes suffix after saturation"',
        'test "memparse applies suffixes before signed clamping"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    "memparse_review_anchors": [
        'test "memparse handles decimal hexadecimal octal and suffixes"',
        'test "memparse keeps original rest when sign is not followed by digits"',
        'test "memparse saturates signed overflow instead of trapping"',
        'test "memparse clamps explicit positive signed overflow"',
        'test "memparse keeps signed values and their trailing rest aligned"',
        'test "memparse consumes suffix after saturation"',
        'test "memparse applies suffixes before signed clamping"',
    ],
    "strscpy_review_anchors": [
        'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
        'test "strscpyPad zero-pads the tail after a short source"',
        'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
        'test "strscpyPad preserves strscpy truncation semantics"',
        'test "strscpy_pad mirrors strscpyPad padding semantics"',
    ],
    "prefix_suffix_review_anchors": [
        'test "strHasPrefix returns the matched prefix length with C-string semantics"',
        'test "strstarts mirrors the header-level prefix helper"',
        'test "strEndsWith honors C-string boundaries"',
    ],
    "sysfs_review_anchors": [
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    ],
    "lookup_review_anchors": [
        'test "matchString finds C-string matches and preserves first-match order"',
        'test "match_string mirrors matchString for empty and matched lists"',
    ],
    "counted_search_review_anchors": [
        'test "strnchr honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    "parity_fixture_keys": [
        "strtobool_y",
        "strtobool_on",
        "strtobool_zero",
        "strtobool_off",
        "strtobool_invalid",
        "strlcpy_len",
        "strlcpy_buffer",
        "skip_spaces",
        "trim_spaces",
        "remove_spaces",
        "replace_char",
        "replace_char_end",
        "replace_char_cstr_end",
        "replace_char_cstr_bytes",
        "memchr_inv_index",
        "memchr_inv_none",
    ],
    "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics"',
    "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
    "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
    "next_safe_step_note": (
        "If this helper lane reopens, keep the helper-local sysfs review anchors aligned "
        "across the string review packet and closure note unless current master later adds "
        "dedicated shared sysfs fixture keys; until then, newline-aware equality and lookup "
        "order remain owned by the direct string tests."
    ),
}

LIST_FIELDS = (
    "helper_test_anchors",
    "memparse_review_anchors",
    "strscpy_review_anchors",
    "prefix_suffix_review_anchors",
    "sysfs_review_anchors",
    "lookup_review_anchors",
    "counted_search_review_anchors",
    "parity_fixture_keys",
)

SCALAR_FIELDS = (
    "basename_review_anchor",
    "trim_nul_review_anchor",
    "memchr_moving_dirty_anchor",
    "phase1_helper_replay_anchor",
    "next_safe_step_note",
)

EXPECTED_SELF_TEST_CASE_COUNT = 19


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def collect_missing_files(root: Path) -> list[str]:
    missing: list[str] = []
    for relative_path in (STRING_HELPER_REL, LANE_NOTE_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            missing.append(f"missing_file:{relative_path.as_posix()}")
    return missing


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_expected_list(value: Any, label: str, expected: list[str]) -> list[str]:
    if value != expected:
        return [f"string_manifest:{label}:expected_current_packet"]
    return []


def require_expected_string(value: Any, label: str, expected: str) -> list[str]:
    if value != expected:
        return [f"string_manifest:{label}:expected_current_packet"]
    return []


def collect_string_review_packet_failures(root: Path) -> list[str]:
    missing = collect_missing_files(root)
    if missing:
        return missing

    helper_text = load_text(root, STRING_HELPER_REL)
    lane_note_text = load_text(root, LANE_NOTE_REL)
    manifest = load_json(root, MANIFEST_REL)

    if not isinstance(manifest, dict):
        return ["string_manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["string_manifest:review_anchors"]

    string_anchors = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_anchors, dict):
        return ["string_manifest:tools/lib/string.zig"]

    missing.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:string_review_rule",
            STRING_REVIEW_RULE_LINE,
        )
    )

    for field in LIST_FIELDS:
        missing.extend(
            require_expected_list(
                string_anchors.get(field),
                field,
                EXPECTED_STRING_ANCHORS[field],
            )
        )

    for field in SCALAR_FIELDS:
        expected = EXPECTED_STRING_ANCHORS[field]
        missing.extend(require_expected_string(string_anchors.get(field), field, expected))

    for anchor in EXPECTED_STRING_ANCHORS["helper_test_anchors"]:
        missing.extend(
            require_exact_occurrence(
                helper_text,
                f"string_helper:{anchor}",
                anchor,
            )
        )

    missing.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:string_next_safe_step_note",
            EXPECTED_STRING_ANCHORS["next_safe_step_note"],
        )
    )

    return missing


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_string_helper_text() -> str:
    return "\n".join(EXPECTED_STRING_ANCHORS["helper_test_anchors"]) + "\n"


def sample_manifest() -> dict[str, Any]:
    return {
        "review_anchors": {
            "tools/lib/string.zig": copy.deepcopy(EXPECTED_STRING_ANCHORS),
        }
    }


def sample_lane_note_text() -> str:
    return (
        "# Phase 1 Host-Helper Lane Sequencing\n\n"
        "## Direct-Anchor Owner Map\n\n"
        f"{STRING_REVIEW_RULE_LINE}\n\n"
        "## Next Bounded Step\n\n"
        f"- {EXPECTED_STRING_ANCHORS['next_safe_step_note']}\n"
    )


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, sample_string_helper_text())
    write_file(root, LANE_NOTE_REL, sample_lane_note_text())
    write_file(root, MANIFEST_REL, json.dumps(sample_manifest(), indent=2) + "\n")


def build_self_test_cases() -> list[tuple[str, str, str]]:
    return [
        ("missing_rule_line", "lane_rule", "remove"),
        ("duplicate_rule_line", "lane_rule", "duplicate"),
        ("missing_helper_anchor", "helper_anchor", "remove"),
        ("missing_next_safe_step", "lane_next_safe_step_note", "remove"),
        ("duplicate_next_safe_step", "lane_next_safe_step_note", "duplicate"),
        *[(f"mutate_{field}", field, "mutate_list") for field in LIST_FIELDS],
        *[(f"mutate_{field}", field, "mutate_scalar") for field in SCALAR_FIELDS],
    ]


def run_self_test() -> int:
    cases = build_self_test_cases()
    if 1 + len(cases) != EXPECTED_SELF_TEST_CASE_COUNT:
        print(
            "self-test:case-count-mismatch:"
            f"expected={EXPECTED_SELF_TEST_CASE_COUNT}:actual={1 + len(cases)}"
        )
        return 1

    with tempfile.TemporaryDirectory(prefix="phase1-string-review-success-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        missing = collect_string_review_packet_failures(root)
        if missing:
            print("self-test:success:unexpected_failures")
            for item in missing:
                print(item)
            return 1

    for name, target, operation in cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-review-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if target == "lane_rule":
                lane_note = root / LANE_NOTE_REL
                text = lane_note.read_text(encoding="utf-8")
                if operation == "remove":
                    lane_note.write_text(text.replace(STRING_REVIEW_RULE_LINE + "\n", "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    lane_note.write_text(
                        text.replace(
                            STRING_REVIEW_RULE_LINE,
                            STRING_REVIEW_RULE_LINE + "\n" + STRING_REVIEW_RULE_LINE,
                            1,
                        ),
                        encoding="utf-8",
                    )
            elif target == "helper_anchor":
                helper_path = root / STRING_HELPER_REL
                text = helper_path.read_text(encoding="utf-8")
                marker = EXPECTED_STRING_ANCHORS["helper_test_anchors"][0]
                helper_path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
            elif target == "lane_next_safe_step_note":
                lane_note = root / LANE_NOTE_REL
                text = lane_note.read_text(encoding="utf-8")
                marker = EXPECTED_STRING_ANCHORS["next_safe_step_note"]
                if operation == "remove":
                    lane_note.write_text(text.replace(marker, "", 1), encoding="utf-8")
                elif operation == "duplicate":
                    lane_note.write_text(
                        text.replace(marker, marker + "\n" + marker, 1),
                        encoding="utf-8",
                    )
            else:
                manifest_path = root / MANIFEST_REL
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                string_anchors = manifest["review_anchors"]["tools/lib/string.zig"]
                if operation == "mutate_list":
                    string_anchors[target] = string_anchors[target][1:]
                elif operation == "mutate_scalar":
                    string_anchors[target] = string_anchors[target] + " drift"
                manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            missing = collect_string_review_packet_failures(root)
            if not missing:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("self-test:ok")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    missing = collect_string_review_packet_failures(repo_root(args.root))
    if missing:
        for item in missing:
            print(item)
        return 1

    print("phase1-string-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

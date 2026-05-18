#!/usr/bin/env python3
"""Guard the Phase 1 string review packet against helper, manifest, and lane-note drift."""

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
    "`scripts/zigux/check-phase1-string-review-packet.py`; the restored "
    "`Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` "
    "companions are now live broader reminder evidence on current `master`, but string "
    "should stay parked on the helper-local sysfs review anchors unless those direct "
    "string surfaces drift."
)

COUNTED_SEARCH_REVIEW_RULE_LINE = (
    "- The counted-search owner term here also covers the current `strnchrNul()` and "
    "`strnchrnul()` match-or-NUL boundary anchor already cataloged in "
    "`zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads "
    "should keep that helper-local boundary proof inside the same counted-search packet "
    "instead of treating it as an unowned follow-up beside `strnchr()`."
)

EXPECTED_STRING_SOURCE_SYMBOLS = [
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
]

EXPECTED_STRING_PACKET = {
    "helper_test_anchors": [
        'test "strtobool accepts common Linux forms"',
        'test "strlcpy copies and returns the source length"',
        'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
        'test "strscpyPad zero-pads the tail after a short source"',
        'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
        'test "strscpyPad preserves strscpy truncation semantics"',
        'test "strscpy_pad mirrors strscpyPad padding semantics"',
        'test "strscpy and strscpyPad keep one-byte destinations terminated"',
        'test "streq matches C-string equality semantics"',
        'test "skip trim remove and replace spaces work in place"',
        'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
        'test "strreplace mirrors replaceChar C-string semantics"',
        'test "strHasPrefix returns the matched prefix length with C-string semantics"',
        'test "strHasSuffix returns the matched suffix length with C-string semantics"',
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
    "memparse_review_summary": (
        "helper-local memparse safety anchors stay explicit through the direct string tests so "
        "sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split "
        "aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of "
        "trapping, and suffixes are still consumed after saturation"
    ),
    "prefix_suffix_review_anchors": [
        'test "strHasPrefix returns the matched prefix length with C-string semantics"',
        'test "strHasSuffix returns the matched suffix length with C-string semantics"',
        'test "strstarts mirrors the header-level prefix helper"',
        'test "strEndsWith honors C-string boundaries"',
    ],
    "prefix_suffix_review_summary": (
        "helper-local prefix and suffix boundary anchors stay explicit through the direct string "
        "tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity "
        "rather than dedicated prefix or suffix fixture fields, so strHasPrefix and str_has_prefix "
        "plus strHasSuffix and str_has_suffix plus strstarts plus strEndsWith and str_ends_with plus strends remain review-visible at "
        "the helper surface"
    ),
    "sysfs_review_anchors": [
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    ],
    "sysfs_review_summary": (
        "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through "
        "the direct string tests because the shared Phase 1 replay still carries no dedicated "
        "sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and "
        "sysfs_match_string remain review-visible at the helper surface"
    ),
    "lookup_review_anchors": [
        'test "matchString finds C-string matches and preserves first-match order"',
        'test "match_string mirrors matchString for empty and matched lists"',
    ],
    "lookup_review_summary": (
        "helper-local string lookup anchors stay explicit through the direct string tests because "
        "the shared Phase 1 replay still does not carry dedicated matchString() or "
        "match_string() fixture keys, so C-string list lookup order and the Linux-style alias "
        "remain review-visible at the helper surface"
    ),
    "strscpy_review_anchors": [
        'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
        'test "strscpyPad zero-pads the tail after a short source"',
        'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
        'test "strscpyPad preserves strscpy truncation semantics"',
        'test "strscpy_pad mirrors strscpyPad padding semantics"',
        'test "strscpy and strscpyPad keep one-byte destinations terminated"',
    ],
    "strscpy_review_summary": (
        "helper-local string copy-and-pad anchors stay explicit through the direct string tests "
        "because the shared Phase 1 replay still does not carry dedicated strscpy() or "
        "strscpyPad() fixture keys"
    ),
    "counted_search_review_anchors": [
        'test "strnchr honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    "strnchr_review_anchor": 'test "strnchr honors count and C-string boundaries"',
    "strnchrnul_review_anchor": 'test "strnchrNul returns the first match, NUL, or count boundary"',
    "strnchr_review_summary": (
        "the direct counted-search follow-up stays explicit because the shared Phase 1 replay "
        "still does not carry dedicated counted-search fixture keys, so strnchr() count-limited "
        "scanning and strnchrNul() or strnchrnul() match-or-NUL boundary behavior remain owned "
        "by the helper-local anchors"
    ),
    "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics"',
    "basename_review_summary": (
        "helper-local basename path-tail anchor stays explicit through the direct string tests "
        "because the shared Phase 1 replay still does not carry dedicated kbasename fixture keys, "
        "so final path-component extraction at the first C-string terminator remains review-visible "
        "at the helper surface"
    ),
    "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "trim_nul_review_summary": (
        "the direct trim follow-up stays explicit because the shared Phase 1 string fixture "
        "records the trimmed bytes but not the preserved tail bytes beyond the first embedded "
        "terminator"
    ),
    "phase1_trim_cstr_replay_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "phase1_trim_cstr_replay_summary": (
        "the shared Phase 1 string replay still only locks the plain trailing-whitespace "
        "trimSpaces bytes from the committed fixture, while the direct helper-local trim "
        "follow-up keeps embedded-NUL trimming for trimSpaces and strim plus strstrip and "
        "preserved tail-byte review explicit because the shared packet still does not exercise "
        "every trim alias or every post-NUL byte position"
    ),
    "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
    "memchr_moving_dirty_review_summary": (
        "the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins "
        "one fixed dirty index and the clean case, but not the moving earliest-mismatch ownership "
        "as later dirty bytes become the next live divergence"
    ),
    "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
    "shared_replace_char_cstr_review_summary": (
        "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, "
        "trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated "
        "embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without "
        "widening helper-local memparse ownership"
    ),
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
    "next_safe_step_note": (
        "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across "
        "the string review packet and this lane note unless dedicated shared sysfs fixture keys "
        "land; do not reopen missing closure-side validator names by default."
    ),
}

LIST_FIELDS = (
    "helper_test_anchors",
    "memparse_review_anchors",
    "prefix_suffix_review_anchors",
    "sysfs_review_anchors",
    "lookup_review_anchors",
    "strscpy_review_anchors",
    "counted_search_review_anchors",
    "parity_fixture_keys",
)

SCALAR_FIELDS = (
    "memparse_review_summary",
    "prefix_suffix_review_summary",
    "sysfs_review_summary",
    "lookup_review_summary",
    "strscpy_review_summary",
    "strnchr_review_anchor",
    "strnchrnul_review_anchor",
    "strnchr_review_summary",
    "basename_review_anchor",
    "basename_review_summary",
    "trim_nul_review_anchor",
    "trim_nul_review_summary",
    "phase1_trim_cstr_replay_anchor",
    "phase1_trim_cstr_replay_summary",
    "memchr_moving_dirty_anchor",
    "memchr_moving_dirty_review_summary",
    "phase1_helper_replay_anchor",
    "shared_replace_char_cstr_review_summary",
    "next_safe_step_note",
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> Any:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_list(value: Any, label: str, expected: list[str]) -> list[str]:
    if value != expected:
        return [f"string_manifest:{label}:expected_current_packet"]
    return []


def require_exact_string(value: Any, label: str, expected: str) -> list[str]:
    if value != expected:
        return [f"string_manifest:{label}:expected_current_packet"]
    return []


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (STRING_HELPER_REL, LANE_NOTE_REL, MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    lane_note_text = load_text(root, LANE_NOTE_REL)
    manifest = load_json(root, MANIFEST_REL)

    review_anchors = manifest.get("review_anchors") if isinstance(manifest, dict) else None
    if not isinstance(review_anchors, dict):
        return ["string_manifest:review_anchors"]
    string_packet = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_packet, dict):
        return ["string_manifest:tools/lib/string.zig"]

    failures.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:string_review_rule",
            STRING_REVIEW_RULE_LINE,
        )
    )
    failures.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:counted_search_review_rule",
            COUNTED_SEARCH_REVIEW_RULE_LINE,
        )
    )
    failures.extend(
        require_exact_occurrence(
            lane_note_text,
            "lane_note:string_next_safe_step_note",
            EXPECTED_STRING_PACKET["next_safe_step_note"],
        )
    )

    for field in LIST_FIELDS:
        failures.extend(
            require_exact_list(string_packet.get(field), field, EXPECTED_STRING_PACKET[field])
        )
    for field in SCALAR_FIELDS:
        failures.extend(
            require_exact_string(string_packet.get(field), field, EXPECTED_STRING_PACKET[field])
        )

    for symbol in EXPECTED_STRING_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol)
        )

    for anchor in EXPECTED_STRING_PACKET["helper_test_anchors"]:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor)
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        STRING_HELPER_REL,
        "\n".join(EXPECTED_STRING_SOURCE_SYMBOLS + EXPECTED_STRING_PACKET["helper_test_anchors"]) + "\n",
    )
    write_file(
        root,
        LANE_NOTE_REL,
        "# sample\n\n"
        + STRING_REVIEW_RULE_LINE
        + "\n\n"
        + COUNTED_SEARCH_REVIEW_RULE_LINE
        + "\n\n- "
        + EXPECTED_STRING_PACKET["next_safe_step_note"]
        + "\n",
    )
    write_file(
        root,
        MANIFEST_REL,
        json.dumps(
            {"review_anchors": {"tools/lib/string.zig": copy.deepcopy(EXPECTED_STRING_PACKET)}},
            indent=2,
        )
        + "\n",
    )


def run_self_test() -> int:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="phase1-string-review-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for item in failures:
                print(item)
            return 1
        case_count += 1

    mutation_specs = [
        ("lane_rule_removed", "lane_rule", "remove"),
        ("lane_rule_duplicated", "lane_rule", "duplicate"),
        ("counted_search_rule_removed", "counted_search_rule", "remove"),
        ("counted_search_rule_duplicated", "counted_search_rule", "duplicate"),
        ("next_safe_step_removed", "next_safe_step", "remove"),
        ("next_safe_step_duplicated", "next_safe_step", "duplicate"),
    ]
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("source_symbol", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_STRING_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_STRING_PACKET["helper_test_anchors"])
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend((f"{field}_mutated", field, "manifest") for field in LIST_FIELDS)
    mutation_specs.extend((f"{field}_mutated", field, "manifest") for field in SCALAR_FIELDS)

    for name, target, kind in mutation_specs:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-review-{name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if kind in {"remove", "duplicate"}:
                if target == "lane_rule":
                    path = root / LANE_NOTE_REL
                    text = path.read_text(encoding="utf-8")
                    if kind == "remove":
                        text = text.replace(STRING_REVIEW_RULE_LINE + "\n", "", 1)
                    else:
                        text = text.replace(
                            STRING_REVIEW_RULE_LINE,
                            STRING_REVIEW_RULE_LINE + "\n" + STRING_REVIEW_RULE_LINE,
                            1,
                        )
                    path.write_text(text, encoding="utf-8")
                elif target == "counted_search_rule":
                    path = root / LANE_NOTE_REL
                    text = path.read_text(encoding="utf-8")
                    if kind == "remove":
                        text = text.replace(COUNTED_SEARCH_REVIEW_RULE_LINE + "\n", "", 1)
                    else:
                        text = text.replace(
                            COUNTED_SEARCH_REVIEW_RULE_LINE,
                            COUNTED_SEARCH_REVIEW_RULE_LINE + "\n" + COUNTED_SEARCH_REVIEW_RULE_LINE,
                            1,
                        )
                    path.write_text(text, encoding="utf-8")
                elif target == "next_safe_step":
                    path = root / LANE_NOTE_REL
                    marker = EXPECTED_STRING_PACKET["next_safe_step_note"]
                    text = path.read_text(encoding="utf-8")
                    if kind == "remove":
                        text = text.replace(marker, "", 1)
                    else:
                        text = text.replace(marker, marker + "\n" + marker, 1)
                    path.write_text(text, encoding="utf-8")
                elif isinstance(target, tuple) and target[0] == "source_symbol":
                    path = root / STRING_HELPER_REL
                    marker = target[1]
                    text = path.read_text(encoding="utf-8")
                    if kind == "remove":
                        text = text.replace(marker + "\n", "", 1)
                    else:
                        text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                    path.write_text(text, encoding="utf-8")
                else:
                    path = root / STRING_HELPER_REL
                    assert isinstance(target, tuple) and target[0] == "helper_anchor"
                    marker = target[1]
                    text = path.read_text(encoding="utf-8")
                    if kind == "remove":
                        text = text.replace(marker + "\n", "", 1)
                    else:
                        text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                    path.write_text(text, encoding="utf-8")
            else:
                path = root / MANIFEST_REL
                manifest = json.loads(path.read_text(encoding="utf-8"))
                packet = manifest["review_anchors"]["tools/lib/string.zig"]
                if isinstance(packet[target], list):
                    packet[target] = packet[target][1:]
                else:
                    packet[target] = packet[target] + " drift"
                path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{name}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for item in failures:
            print(item)
        return 1

    print("phase1-string-review-packet:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
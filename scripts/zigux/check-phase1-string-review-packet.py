#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

SELF_PATH = Path(__file__).resolve()
ROOT = SELF_PATH.parents[2] if len(SELF_PATH.parents) >= 3 else Path.cwd()

REQUIRED_FILES = [
    "Documentation/zigux/phase1-closure.md",
    "Documentation/zigux/phase1-host-helper-lane-sequencing.md",
    "tools/lib/string.zig",
    "zigux/tests/phase1_helpers.zig",
    "zigux/tests/fixtures/phase1_helper_manifest.json",
    "zigux/tests/fixtures/phase1_helpers.json",
]

EXPECTED_HELPER_TEST_ANCHORS = [
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
    'test "memparse handles decimal hexadecimal octal and suffixes"',
    'test "memparse keeps original rest when sign is not followed by digits"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "memparse clamps explicit positive signed overflow"',
    'test "memparse keeps signed values and their trailing rest aligned"',
    'test "memparse consumes suffix after saturation"',
    'test "memparse applies suffixes before signed clamping"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
]

EXPECTED_STRSCPY_REVIEW_ANCHORS = [
    'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
    'test "strscpyPad zero-pads the tail after a short source"',
    'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
    'test "strscpyPad preserves strscpy truncation semantics"',
    'test "strscpy_pad mirrors strscpyPad padding semantics"',
]

EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS = [
    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
    'test "strstarts mirrors the header-level prefix helper"',
    'test "strEndsWith honors C-string boundaries"',
]

EXPECTED_LOOKUP_REVIEW_ANCHORS = [
    'test "matchString finds C-string matches and preserves first-match order"',
    'test "match_string mirrors matchString for empty and matched lists"',
]

EXPECTED_SYSFS_REVIEW_ANCHORS = [
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
]

EXPECTED_MEMPARSE_REVIEW_ANCHORS = [
    'test "memparse handles decimal hexadecimal octal and suffixes"',
    'test "memparse keeps original rest when sign is not followed by digits"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "memparse clamps explicit positive signed overflow"',
    'test "memparse keeps signed values and their trailing rest aligned"',
    'test "memparse consumes suffix after saturation"',
    'test "memparse applies suffixes before signed clamping"',
]

EXPECTED_COUNTED_SEARCH_REVIEW_ANCHORS = [
    'test "strnchr honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
]

EXPECTED_STRNCHR_REVIEW_ANCHOR = 'test "strnchr honors count and C-string boundaries"'
EXPECTED_STRNCHRNUL_REVIEW_ANCHOR = 'test "strnchrNul returns the first match, NUL, or count boundary"'
EXPECTED_TRIM_NUL_REVIEW_ANCHOR = 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"'
EXPECTED_MEMCHR_MOVING_DIRTY_ANCHOR = 'test "memchrInv follows the earliest dirty byte as long buffers change"'
EXPECTED_PHASE1_HELPER_REPLAY_ANCHOR = 'test "phase 1 string replaceChar stops at embedded NUL"'
EXPECTED_PHASE1_TRIM_CSTR_REPLAY_ANCHOR = 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"'

EXPECTED_PARITY_FIXTURE_KEYS = [
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
]

EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY = (
    "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared "
    "Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields, "
    "so strHasPrefix and str_has_prefix plus strstarts plus strEndsWith and str_ends_with plus strends remain review-visible "
    "at the helper surface"
)
EXPECTED_LOOKUP_REVIEW_SUMMARY = (
    "helper-local string lookup anchors stay explicit through the direct string tests because the shared Phase 1 replay still "
    "does not carry dedicated matchString or match_string fixture keys, so C-string list lookup order and the Linux-style "
    "alias remain review-visible at the helper surface"
)
EXPECTED_SYSFS_REVIEW_SUMMARY = (
    "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because "
    "the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus "
    "sysfsMatchString and sysfs_match_string remain review-visible at the helper surface"
)
EXPECTED_STRSCPY_REVIEW_SUMMARY = (
    "helper-local string copy-and-pad anchors stay explicit through the direct string tests because the shared Phase 1 "
    "replay still does not carry dedicated strscpy or strscpyPad fixture keys"
)
EXPECTED_STRNCHR_REVIEW_SUMMARY = (
    "the direct counted-search follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated "
    "counted-search fixture keys, so strnchr() count-limited scanning and strnchrNul() or strnchrnul() match-or-NUL "
    "boundary behavior remain owned by the helper-local anchors"
)
EXPECTED_TRIM_NUL_REVIEW_SUMMARY = (
    "the direct trim follow-up stays explicit because the shared Phase 1 string fixture records the trimmed bytes but not "
    "the preserved tail bytes beyond the first embedded terminator"
)
EXPECTED_PHASE1_TRIM_CSTR_REPLAY_SUMMARY = (
    "the shared Phase 1 string replay still only locks the plain trailing-whitespace trimSpaces bytes from the committed "
    "fixture, while the direct helper-local trim follow-up keeps embedded-NUL trimming for trimSpaces and strim plus "
    "strstrip and preserved tail-byte review explicit because the shared packet still does not exercise every trim alias "
    "or every post-NUL byte position"
)
EXPECTED_MEMCHR_MOVING_DIRTY_REVIEW_SUMMARY = (
    "the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins one fixed dirty index and the "
    "clean case, but not the moving earliest-mismatch ownership as later dirty bytes become the next live divergence"
)
EXPECTED_MEMPARSE_REVIEW_SUMMARY = (
    "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input "
    "preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit "
    "signed overflow clamp instead of trapping, and suffixes are still consumed after saturation"
)
EXPECTED_SHARED_REPLACE_CHAR_CSTR_REVIEW_SUMMARY = (
    "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, "
    "and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop "
    "rule explicit without widening helper-local memparse ownership"
)
EXPECTED_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and "
    "closure note unless current master later adds dedicated shared sysfs fixture keys; until then, newline-aware equality "
    "and lookup order remain owned by the direct string tests."
)

EXPECTED_CLOSURE_MARKERS = [
    "PHASE1_STRING_MEMPARSE_REVIEW=helper-local memparse safety anchors stay explicit through the direct string tests and the Phase 1 helper manifest so sign-prefixed invalid input preserves rest, signed inputs keep trailing-rest splits aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation",
    "PHASE1_STRING_REVIEW_PACKET=helper-local string tests and the shared embedded-NUL replay stay explicit so the bounded Phase 1 string surface keeps its direct review anchors, committed C-string replacement bytes, and parity fixture keys",
    "PHASE1_STRING_STRSCPY_REVIEW=helper-local string copy-and-pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strscpy or strscpyPad fixture keys",
    "PHASE1_STRING_LOOKUP_AND_STRNCHR_REVIEW=helper-local string C-string list lookup and counted-search anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated matchString or match_string or strnchr fixture keys",
]

EXPECTED_LANE_NOTE_MARKER = (
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() "
    "copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup "
    "order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or "
    "moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep "
    "the helper-local sysfs review anchors aligned across the string review packet and closure note unless dedicated "
    "shared sysfs fixture keys land; do not reopen a generic closure-validator pass`"
)


def repo_root(root_arg: str | None) -> Path:
    return Path(root_arg).resolve() if root_arg else ROOT


def collect_missing_files(root: Path) -> list[str]:
    return [rel for rel in REQUIRED_FILES if not (root / rel).exists()]


def load_json(path: Path, label: str) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [f"{label}:json_decode_error:{exc.msg}:line={exc.lineno}:column={exc.colno}"]


def extract_test_titles(text: str) -> list[str]:
    titles: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith('test "') and stripped.endswith("{"):
            titles.append(stripped[:-1].rstrip())
    return titles


def collect_exact_count_markers(text: str, label: str, markers: list[str]) -> list[str]:
    missing: list[str] = []
    for marker in markers:
        count = text.count(marker)
        if count != 1:
            missing.append(f"{label}:{marker}:expected=1:actual={count}")
    return missing


def collect_manifest_issues(manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["phase1_string_manifest:json_object"]

    review_anchors = manifest.get("review_anchors")
    if not isinstance(review_anchors, dict):
        return ["phase1_string_manifest:review_anchors"]

    string_anchors = review_anchors.get("tools/lib/string.zig")
    if not isinstance(string_anchors, dict):
        return ["phase1_string_manifest:tools/lib/string.zig"]

    issues: list[str] = []

    expected_lists = {
        "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
        "strscpy_review_anchors": EXPECTED_STRSCPY_REVIEW_ANCHORS,
        "prefix_suffix_review_anchors": EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS,
        "lookup_review_anchors": EXPECTED_LOOKUP_REVIEW_ANCHORS,
        "sysfs_review_anchors": EXPECTED_SYSFS_REVIEW_ANCHORS,
        "memparse_review_anchors": EXPECTED_MEMPARSE_REVIEW_ANCHORS,
        "counted_search_review_anchors": EXPECTED_COUNTED_SEARCH_REVIEW_ANCHORS,
        "parity_fixture_keys": EXPECTED_PARITY_FIXTURE_KEYS,
    }
    for key, expected in expected_lists.items():
        if string_anchors.get(key) != expected:
            issues.append(f"phase1_string_manifest:{key}")

    expected_scalars = {
        "strnchr_review_anchor": EXPECTED_STRNCHR_REVIEW_ANCHOR,
        "strnchrnul_review_anchor": EXPECTED_STRNCHRNUL_REVIEW_ANCHOR,
        "trim_nul_review_anchor": EXPECTED_TRIM_NUL_REVIEW_ANCHOR,
        "memchr_moving_dirty_anchor": EXPECTED_MEMCHR_MOVING_DIRTY_ANCHOR,
        "phase1_helper_replay_anchor": EXPECTED_PHASE1_HELPER_REPLAY_ANCHOR,
        "phase1_trim_cstr_replay_anchor": EXPECTED_PHASE1_TRIM_CSTR_REPLAY_ANCHOR,
        "prefix_suffix_review_summary": EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY,
        "lookup_review_summary": EXPECTED_LOOKUP_REVIEW_SUMMARY,
        "sysfs_review_summary": EXPECTED_SYSFS_REVIEW_SUMMARY,
        "strscpy_review_summary": EXPECTED_STRSCPY_REVIEW_SUMMARY,
        "strnchr_review_summary": EXPECTED_STRNCHR_REVIEW_SUMMARY,
        "trim_nul_review_summary": EXPECTED_TRIM_NUL_REVIEW_SUMMARY,
        "phase1_trim_cstr_replay_summary": EXPECTED_PHASE1_TRIM_CSTR_REPLAY_SUMMARY,
        "memchr_moving_dirty_review_summary": EXPECTED_MEMCHR_MOVING_DIRTY_REVIEW_SUMMARY,
        "memparse_review_summary": EXPECTED_MEMPARSE_REVIEW_SUMMARY,
        "shared_replace_char_cstr_review_summary": EXPECTED_SHARED_REPLACE_CHAR_CSTR_REVIEW_SUMMARY,
        "next_safe_step_note": EXPECTED_NEXT_SAFE_STEP_NOTE,
    }
    for key, expected in expected_scalars.items():
        if string_anchors.get(key) != expected:
            issues.append(f"phase1_string_manifest:{key}")

    return issues


def collect_shared_fixture_issues(shared_fixture: object) -> list[str]:
    if not isinstance(shared_fixture, dict):
        return ["phase1_string_shared_fixture:json_object"]

    string_fixture = shared_fixture.get("string")
    if not isinstance(string_fixture, dict):
        return ["phase1_string_shared_fixture:string"]

    if sorted(string_fixture.keys()) != sorted(EXPECTED_PARITY_FIXTURE_KEYS):
        return ["phase1_string_shared_fixture:parity_fixture_keys"]

    return []


def collect_source_issues(source_text: str) -> list[str]:
    actual_titles = extract_test_titles(source_text)
    if actual_titles != EXPECTED_HELPER_TEST_ANCHORS:
        return ["phase1_string_source:helper_test_anchors"]
    return []


def collect_shared_replay_issues(shared_replay_text: str) -> list[str]:
    return collect_exact_count_markers(
        shared_replay_text,
        "phase1_string_shared_replay",
        [
            EXPECTED_PHASE1_HELPER_REPLAY_ANCHOR,
            EXPECTED_PHASE1_TRIM_CSTR_REPLAY_ANCHOR,
        ],
    )


def collect_closure_issues(closure_text: str) -> list[str]:
    return collect_exact_count_markers(
        closure_text,
        "phase1_string_closure",
        EXPECTED_CLOSURE_MARKERS,
    )


def collect_lane_note_issues(lane_note_text: str) -> list[str]:
    return collect_exact_count_markers(
        lane_note_text,
        "phase1_string_lane_note",
        [EXPECTED_LANE_NOTE_MARKER],
    )


def collect_missing_markers(root: Path) -> list[str]:
    source_text = (root / "tools/lib/string.zig").read_text(encoding="utf-8")
    shared_replay_text = (root / "zigux/tests/phase1_helpers.zig").read_text(encoding="utf-8")
    closure_text = (root / "Documentation/zigux/phase1-closure.md").read_text(encoding="utf-8")
    lane_note_text = (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").read_text(encoding="utf-8")
    manifest, manifest_errors = load_json(
        root / "zigux/tests/fixtures/phase1_helper_manifest.json",
        "phase1_string_manifest",
    )
    shared_fixture, shared_fixture_errors = load_json(
        root / "zigux/tests/fixtures/phase1_helpers.json",
        "phase1_string_shared_fixture",
    )

    issues: list[str] = []
    issues.extend(manifest_errors)
    issues.extend(shared_fixture_errors)
    issues.extend(collect_source_issues(source_text))
    issues.extend(collect_shared_replay_issues(shared_replay_text))
    issues.extend(collect_closure_issues(closure_text))
    issues.extend(collect_lane_note_issues(lane_note_text))
    if manifest is not None:
        issues.extend(collect_manifest_issues(manifest))
    if shared_fixture is not None:
        issues.extend(collect_shared_fixture_issues(shared_fixture))
    return issues


def make_fixture_root(root: Path) -> None:
    for rel in REQUIRED_FILES:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n", encoding="utf-8")

    helper_source = "\n\n".join(f"{title} {{" for title in EXPECTED_HELPER_TEST_ANCHORS) + "\n"
    (root / "tools/lib/string.zig").write_text(helper_source, encoding="utf-8")

    (root / "zigux/tests/phase1_helpers.zig").write_text(
        "\n".join(
            [
                EXPECTED_PHASE1_HELPER_REPLAY_ANCHOR + " {",
                EXPECTED_PHASE1_TRIM_CSTR_REPLAY_ANCHOR + " {",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    (root / "Documentation/zigux/phase1-closure.md").write_text(
        "\n".join(EXPECTED_CLOSURE_MARKERS) + "\n",
        encoding="utf-8",
    )
    (root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md").write_text(
        EXPECTED_LANE_NOTE_MARKER + "\n",
        encoding="utf-8",
    )

    manifest = {
        "review_anchors": {
            "tools/lib/string.zig": {
                "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
                "strscpy_review_anchors": EXPECTED_STRSCPY_REVIEW_ANCHORS,
                "prefix_suffix_review_anchors": EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS,
                "lookup_review_anchors": EXPECTED_LOOKUP_REVIEW_ANCHORS,
                "sysfs_review_anchors": EXPECTED_SYSFS_REVIEW_ANCHORS,
                "memparse_review_anchors": EXPECTED_MEMPARSE_REVIEW_ANCHORS,
                "counted_search_review_anchors": EXPECTED_COUNTED_SEARCH_REVIEW_ANCHORS,
                "strnchr_review_anchor": EXPECTED_STRNCHR_REVIEW_ANCHOR,
                "strnchrnul_review_anchor": EXPECTED_STRNCHRNUL_REVIEW_ANCHOR,
                "trim_nul_review_anchor": EXPECTED_TRIM_NUL_REVIEW_ANCHOR,
                "memchr_moving_dirty_anchor": EXPECTED_MEMCHR_MOVING_DIRTY_ANCHOR,
                "phase1_helper_replay_anchor": EXPECTED_PHASE1_HELPER_REPLAY_ANCHOR,
                "phase1_trim_cstr_replay_anchor": EXPECTED_PHASE1_TRIM_CSTR_REPLAY_ANCHOR,
                "parity_fixture_keys": EXPECTED_PARITY_FIXTURE_KEYS,
                "prefix_suffix_review_summary": EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY,
                "lookup_review_summary": EXPECTED_LOOKUP_REVIEW_SUMMARY,
                "sysfs_review_summary": EXPECTED_SYSFS_REVIEW_SUMMARY,
                "strscpy_review_summary": EXPECTED_STRSCPY_REVIEW_SUMMARY,
                "strnchr_review_summary": EXPECTED_STRNCHR_REVIEW_SUMMARY,
                "trim_nul_review_summary": EXPECTED_TRIM_NUL_REVIEW_SUMMARY,
                "phase1_trim_cstr_replay_summary": EXPECTED_PHASE1_TRIM_CSTR_REPLAY_SUMMARY,
                "memchr_moving_dirty_review_summary": EXPECTED_MEMCHR_MOVING_DIRTY_REVIEW_SUMMARY,
                "memparse_review_summary": EXPECTED_MEMPARSE_REVIEW_SUMMARY,
                "shared_replace_char_cstr_review_summary": EXPECTED_SHARED_REPLACE_CHAR_CSTR_REVIEW_SUMMARY,
                "next_safe_step_note": EXPECTED_NEXT_SAFE_STEP_NOTE,
            }
        }
    }
    (root / "zigux/tests/fixtures/phase1_helper_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )

    shared_fixture = {
        "string": {key: None for key in EXPECTED_PARITY_FIXTURE_KEYS},
    }
    (root / "zigux/tests/fixtures/phase1_helpers.json").write_text(
        json.dumps(shared_fixture, indent=2) + "\n",
        encoding="utf-8",
    )


def run_self_test() -> None:
    case_count = 0
    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_packet_") as tmp_dir:
        root = Path(tmp_dir)
        make_fixture_root(root)
        assert collect_missing_files(root) == []
        assert collect_missing_markers(root) == []
        case_count += 2

        source_path = root / "tools/lib/string.zig"
        original_source = source_path.read_text(encoding="utf-8")
        source_path.write_text(original_source.replace(EXPECTED_HELPER_TEST_ANCHORS[-1] + " {\n", "", 1), encoding="utf-8")
        assert "phase1_string_source:helper_test_anchors" in collect_missing_markers(root)
        source_path.write_text(original_source, encoding="utf-8")
        case_count += 1

        shared_replay_path = root / "zigux/tests/phase1_helpers.zig"
        original_replay = shared_replay_path.read_text(encoding="utf-8")
        shared_replay_path.write_text(
            original_replay.replace(EXPECTED_PHASE1_HELPER_REPLAY_ANCHOR + " {\n", "", 1),
            encoding="utf-8",
        )
        assert any(item.startswith("phase1_string_shared_replay:") for item in collect_missing_markers(root))
        shared_replay_path.write_text(original_replay, encoding="utf-8")
        case_count += 1

        closure_path = root / "Documentation/zigux/phase1-closure.md"
        original_closure = closure_path.read_text(encoding="utf-8")
        closure_path.write_text(original_closure.replace(EXPECTED_CLOSURE_MARKERS[0] + "\n", "", 1), encoding="utf-8")
        assert any(item.startswith("phase1_string_closure:") for item in collect_missing_markers(root))
        closure_path.write_text(original_closure, encoding="utf-8")
        case_count += 1

        closure_path.write_text(original_closure.replace(EXPECTED_CLOSURE_MARKERS[-1] + "\n", "", 1), encoding="utf-8")
        assert any(item.startswith("phase1_string_closure:") for item in collect_missing_markers(root))
        closure_path.write_text(original_closure, encoding="utf-8")
        case_count += 1

        lane_note_path = root / "Documentation/zigux/phase1-host-helper-lane-sequencing.md"
        lane_note_path.write_text("", encoding="utf-8")
        assert any(item.startswith("phase1_string_lane_note:") for item in collect_missing_markers(root))
        lane_note_path.write_text(EXPECTED_LANE_NOTE_MARKER + "\n", encoding="utf-8")
        case_count += 1

        manifest_path = root / "zigux/tests/fixtures/phase1_helper_manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["sysfs_review_anchors"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_string_manifest:sysfs_review_anchors" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["next_safe_step_note"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        assert "phase1_string_manifest:next_safe_step_note" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        manifest_path.write_text("{\n", encoding="utf-8")
        assert any(item.startswith("phase1_string_manifest:json_decode_error:") for item in collect_missing_markers(root))
        make_fixture_root(root)
        case_count += 1

        shared_fixture_path = root / "zigux/tests/fixtures/phase1_helpers.json"
        shared_fixture = json.loads(shared_fixture_path.read_text(encoding="utf-8"))
        shared_fixture["string"].pop(EXPECTED_PARITY_FIXTURE_KEYS[-1])
        shared_fixture_path.write_text(json.dumps(shared_fixture, indent=2) + "\n", encoding="utf-8")
        assert "phase1_string_shared_fixture:parity_fixture_keys" in collect_missing_markers(root)
        make_fixture_root(root)
        case_count += 1

        shared_fixture_path.write_text("{\n", encoding="utf-8")
        assert any(item.startswith("phase1_string_shared_fixture:json_decode_error:") for item in collect_missing_markers(root))
        make_fixture_root(root)
        case_count += 1

        source_path.unlink()
        assert collect_missing_files(root) == ["tools/lib/string.zig"]
        make_fixture_root(root)
        case_count += 1

    print("PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_REVIEW_PACKET_SELF_TEST_CASE_COUNT={case_count}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the bounded Phase 1 string review packet across helper anchors, manifest summaries, shared replay, shared fixture keys, and next-step note.",
    )
    parser.add_argument("--self-test", action="store_true", help="Run built-in checker self-tests.")
    parser.add_argument("--root", help="Validate an alternate Zigux tree root.")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        return 0

    root = repo_root(args.root)
    missing_files = collect_missing_files(root)
    if missing_files:
        print("PHASE1_STRING_REVIEW_PACKET=fail")
        print("MISSING_PHASE1_STRING_REVIEW_PACKET_FILES_START")
        for item in missing_files:
            print(item)
        print("MISSING_PHASE1_STRING_REVIEW_PACKET_FILES_END")
        return 1

    missing_markers = collect_missing_markers(root)
    if missing_markers:
        print("PHASE1_STRING_REVIEW_PACKET=fail")
        print("MISSING_PHASE1_STRING_REVIEW_PACKET_MARKERS_START")
        for item in missing_markers:
            print(item)
        print("MISSING_PHASE1_STRING_REVIEW_PACKET_MARKERS_END")
        return 1

    print("PHASE1_STRING_REVIEW_PACKET=pass")
    print(f"PHASE1_STRING_REVIEW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print("PHASE1_STRING_REVIEW_PACKET_REQUIRED_MARKER_COUNT=25")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

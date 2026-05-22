#!/usr/bin/env python3
"""Guard the Phase 1 string helper review packet against helper, manifest, fixture, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
STRING_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
STRING_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

EXPECTED_STRING_SOURCE_SYMBOLS = [
    "pub fn memparse(text: []const u8) MemparseResult {",
    "pub fn strscpy(dest: []u8, src: []const u8) isize {",
    "pub fn strscpyPad(dest: []u8, src: []const u8) isize {",
    "pub fn strscpy_pad(dest: []u8, src: []const u8) isize {",
    "pub fn strEq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn trimSpaces(buf: []u8) []u8 {",
    "pub fn strim(buf: []u8) []u8 {",
    "pub fn strstrip(buf: []u8) []u8 {",
    "pub fn strHasPrefix(buf: []const u8, prefix: []const u8) usize {",
    "pub fn str_has_prefix(buf: []const u8, prefix: []const u8) usize {",
    "pub fn strstarts(buf: []const u8, prefix: []const u8) bool {",
    "pub fn strHasSuffix(buf: []const u8, suffix: []const u8) usize {",
    "pub fn str_has_suffix(buf: []const u8, suffix: []const u8) usize {",
    "pub fn strEndsWith(buf: []const u8, suffix: []const u8) bool {",
    "pub fn str_ends_with(buf: []const u8, suffix: []const u8) bool {",
    "pub fn strends(buf: []const u8, suffix: []const u8) bool {",
    "pub fn kbasename(path: []const u8) []const u8 {",
    "pub fn memchrInv(buf: []const u8, value: u8) ?usize {",
    "pub fn memchr_inv(buf: []const u8, value: u8) ?usize {",
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn __sysfs_match_string(haystack: []const []const u8, count: usize, needle: []const u8) ?usize {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {",
    "pub fn strspn(buf: []const u8, accept: []const u8) usize {",
    "pub fn strcspn(buf: []const u8, reject: []const u8) usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnlen(buf: []const u8, count: usize) usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
    "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
]

EXPECTED_HELPER_TEST_ANCHORS = [
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
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strchr and strrchr return the terminator index when searching for NUL"',
    'test "strpbrk finds the first accepted byte with C-string semantics"',
    'test "strspn counts the accepted prefix with C-string semantics"',
    'test "strcspn counts until the first rejected byte with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
]

EXPECTED_STRING_PACKET = {
    "helper_test_anchors": EXPECTED_HELPER_TEST_ANCHORS,
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
        "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests "
        "because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather "
        "than dedicated prefix or suffix fixture fields, so strHasPrefix and str_has_prefix plus "
        "strHasSuffix and str_has_suffix plus strstarts plus strEndsWith and str_ends_with plus "
        "strends remain review-visible at the helper surface"
    ),
    "lookup_review_anchors": [
        'test "matchString finds C-string matches and preserves first-match order"',
        'test "match_string mirrors matchString for empty and matched lists"',
    ],
    "lookup_review_summary": (
        "helper-local string lookup anchors stay explicit through the direct string tests because the "
        "shared Phase 1 replay still does not carry dedicated matchString() or match_string() fixture "
        "keys, so C-string list lookup order and the Linux-style alias remain review-visible at the "
        "helper surface"
    ),
    "sysfs_review_anchors": [
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    ],
    "sysfs_review_summary": (
        "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the "
        "direct string tests because the shared Phase 1 replay still carries no dedicated sysfs "
        "fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string "
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
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strpbrk finds the first accepted byte with C-string semantics"',
        'test "strspn counts the accepted prefix with C-string semantics"',
        'test "strcspn counts until the first rejected byte with C-string semantics"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    "strnchr_review_anchor": 'test "strnchr honors count and C-string boundaries"',
    "strnchrnul_review_anchor": 'test "strnchrNul returns the first match, NUL, or count boundary"',
    "strnchr_review_summary": (
        "the direct counted-search and C-string search-length follow-up stays explicit because the "
        "shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture "
        "keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte "
        "scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() "
        "count-limited scanning, strnlen() count-clamped length, and strnchrNul() or strnchrnul() "
        "match-or-NUL boundary behavior remain owned by the helper-local anchors"
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
        "the direct trim follow-up stays explicit because the shared Phase 1 string fixture records "
        "the trimmed bytes but not the preserved tail bytes beyond the first embedded terminator"
    ),
    "phase1_trim_cstr_replay_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "phase1_trim_cstr_replay_summary": (
        "the shared Phase 1 string replay still only locks the plain trailing-whitespace trimSpaces "
        "bytes from the committed fixture, while the direct helper-local trim follow-up keeps "
        "embedded-NUL trimming for trimSpaces and strim plus strstrip and preserved tail-byte review "
        "explicit because the shared packet still does not exercise every trim alias or every "
        "post-NUL byte position"
    ),
    "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
    "memchr_moving_dirty_review_summary": (
        "the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins one "
        "fixed dirty index and the clean case, but not the moving earliest-mismatch ownership as later "
        "dirty bytes become the next live divergence"
    ),
    "phase1_helper_replay_anchor": 'test "phase 1 string replaceChar stops at embedded NUL"',
    "shared_replace_char_cstr_review_summary": (
        "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, "
        "removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL "
        "replaceChar follow-up keeps the first-terminator stop rule explicit without widening "
        "helper-local memparse ownership"
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

EXPECTED_STRING_FIXTURE_VALUES = {
    "strtobool_y": True,
    "strtobool_on": True,
    "strtobool_zero": False,
    "strtobool_off": False,
    "strtobool_invalid": 184,
    "strlcpy_len": 5,
    "strlcpy_buffer": "hel",
    "skip_spaces": "hello",
    "trim_spaces": "hi",
    "remove_spaces": "abc",
    "replace_char": "a_b",
    "replace_char_end": 3,
    "replace_char_cstr_end": 2,
    "replace_char_cstr_bytes": [97, 95, 0, 45, 122],
    "memchr_inv_index": 4,
    "memchr_inv_none": True,
}

EXPECTED_STRING_LANE_MARKERS = [
    (
        "lane_direct_owner",
        "`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, "
        "memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality "
        "and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and "
        "sysfs_match_string(), C-string list lookup through matchString() and match_string(), "
        "counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte "
        "memchrInv coverage helper-local while the committed shared replay owns embedded-NUL "
        "replaceChar parity bytes and the current string fixture keys`",
    ),
    (
        "lane_next_safe_step",
        "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside "
        "strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix "
        "boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() "
        "C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-"
        "dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture "
        "drift; keep the helper-local sysfs review anchors aligned across the string review packet "
        "and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing "
        "closure-side validator names by default`",
    ),
    (
        "lane_counted_search_match_or_nul",
        "- The counted-search owner term here also covers the current `strnchrNul()` and "
        "`strnchrnul()` match-or-NUL boundary anchor already cataloged in "
        "`zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should "
        "keep that helper-local boundary proof inside the same counted-search packet instead of "
        "treating it as an unowned follow-up beside `strnchr()`."
    ),
    (
        "lane_counted_search_strspn",
        "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix "
        "anchor review-visible on current `master`, so future string-only rereads should treat "
        "accepted-byte-prefix scanning as part of that helper-local search family instead of "
        "leaving it implicit beside `strpbrk()` and `strnchr()`."
    ),
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def load_json_failure(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def iter_anchor_strings(expected: object) -> list[str]:
    anchors: list[str] = []
    if isinstance(expected, str):
        if expected.startswith('test "'):
            anchors.append(expected)
    elif isinstance(expected, list):
        for item in expected:
            if isinstance(item, str) and item.startswith('test "'):
                anchors.append(item)
    return anchors


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (
        STRING_HELPER_REL,
        STRING_MANIFEST_REL,
        STRING_FIXTURE_REL,
        STRING_LANE_NOTE_REL,
    ):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    lane_text = load_text(root, STRING_LANE_NOTE_REL)
    try:
        manifest = load_json(root, STRING_MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("manifest", exc)]

    try:
        fixture = load_json(root, STRING_FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [load_json_failure("fixture", exc)]

    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]
    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]

    for symbol in EXPECTED_STRING_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol)
        )

    seen_helper_anchors = set(EXPECTED_HELPER_TEST_ANCHORS)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor)
        )

    for key, expected in EXPECTED_STRING_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor in seen_helper_anchors:
                continue
            failures.extend(
                require_exact_occurrence(helper_text, f"string_helper_packet:{key}", anchor)
            )
            seen_helper_anchors.add(anchor)

    for label, marker in EXPECTED_STRING_LANE_MARKERS:
        failures.extend(
            require_exact_occurrence(
                lane_text,
                f"string_lane:{label}",
                marker,
            )
        )

    failures.extend(
        require_exact_value(
            "string_manifest:review_anchors.tools/lib/string.zig.helper_test_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "helper_test_anchors")),
            EXPECTED_HELPER_TEST_ANCHORS,
        )
    )

    for key, expected in EXPECTED_STRING_PACKET.items():
        if key == "helper_test_anchors":
            continue
        failures.extend(
            require_exact_value(
                f"string_manifest:review_anchors.tools/lib/string.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/string.zig", key)),
                expected,
            )
        )

    string_fixture = fixture.get("string")
    if not isinstance(string_fixture, dict):
        return ["string_fixture:expected=dict:actual=missing"]
    for key, expected in EXPECTED_STRING_FIXTURE_VALUES.items():
        failures.extend(
            require_exact_value(
                f"string_fixture:{key}",
                string_fixture.get(key),
                expected,
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    return (
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/string.zig": EXPECTED_STRING_PACKET,
                }
            },
            indent=2,
        )
        + "\n"
    )


def sample_fixture() -> str:
    return json.dumps({"string": EXPECTED_STRING_FIXTURE_VALUES}, indent=2) + "\n"


def sample_lane_note() -> str:
    return "\n".join(marker for _, marker in EXPECTED_STRING_LANE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    helper_lines = list(EXPECTED_STRING_SOURCE_SYMBOLS)
    seen = set(helper_lines)
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        if anchor not in seen:
            helper_lines.append(anchor)
            seen.add(anchor)
    for key, expected in EXPECTED_STRING_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor not in seen:
                helper_lines.append(anchor)
                seen.add(anchor)

    write_file(
        root,
        STRING_HELPER_REL,
        "\n".join(helper_lines) + "\n",
    )
    write_file(root, STRING_MANIFEST_REL, sample_manifest())
    write_file(root, STRING_FIXTURE_REL, sample_fixture())
    write_file(root, STRING_LANE_NOTE_REL, sample_lane_note())


def mutate_json_path(root: Path, relative_path: Path, path: tuple[str, ...]) -> None:
    json_path = root / relative_path
    data = json.loads(json_path.read_text(encoding="utf-8"))
    current = data
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    elif isinstance(value, bool):
        current[final_key] = not value
    elif isinstance(value, int):
        current[final_key] = value + 1
    else:
        current[final_key] = f"{value} drift"
    json_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


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

    mutation_specs = []
    mutation_specs.extend(
        (f"source_symbol_{idx}_{kind}", ("source_symbol", symbol), kind)
        for idx, symbol in enumerate(EXPECTED_STRING_SOURCE_SYMBOLS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (f"helper_anchor_{idx}_{kind}", ("helper_anchor", anchor), kind)
        for idx, anchor in enumerate(EXPECTED_HELPER_TEST_ANCHORS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"packet_anchor_phase1_helper_replay_{kind}",
            ("packet_anchor", EXPECTED_STRING_PACKET["phase1_helper_replay_anchor"]),
            kind,
        )
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"lane_marker_{idx}_{kind}",
            ("lane_marker", marker),
            kind,
        )
        for idx, (_, marker) in enumerate(EXPECTED_STRING_LANE_MARKERS)
        for kind in ("remove", "duplicate")
    )
    mutation_specs.extend(
        (
            f"manifest_{key}",
            ("manifest", ("review_anchors", "tools/lib/string.zig", key)),
            "manifest",
        )
        for key in EXPECTED_STRING_PACKET
    )
    mutation_specs.extend(
        (
            f"fixture_{key}",
            ("fixture", ("string", key)),
            "fixture",
        )
        for key in EXPECTED_STRING_FIXTURE_VALUES
    )
    mutation_specs.append(("manifest_missing_file", ("missing_file", STRING_MANIFEST_REL), "missing_file"))
    mutation_specs.append(("fixture_missing_file", ("missing_file", STRING_FIXTURE_REL), "missing_file"))
    mutation_specs.append(("lane_note_missing_file", ("missing_file", STRING_LANE_NOTE_REL), "missing_file"))
    mutation_specs.append(("manifest_invalid_json", ("invalid_json", STRING_MANIFEST_REL), "invalid_json"))
    mutation_specs.append(("fixture_invalid_json", ("invalid_json", STRING_FIXTURE_REL), "invalid_json"))

    for name, target, kind in mutation_specs:
        safe_name = name.replace("/", "_")
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-review-{safe_name}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)

            if isinstance(target, tuple) and target[0] == "source_symbol":
                path = root / STRING_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "helper_anchor":
                path = root / STRING_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "packet_anchor":
                path = root / STRING_HELPER_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "lane_marker":
                path = root / STRING_LANE_NOTE_REL
                marker = target[1]
                text = path.read_text(encoding="utf-8")
                if kind == "remove":
                    text = text.replace(marker + "\n", "", 1)
                else:
                    text = text.replace(marker + "\n", marker + "\n" + marker + "\n", 1)
                path.write_text(text, encoding="utf-8")
            elif isinstance(target, tuple) and target[0] == "manifest":
                mutate_json_path(root, STRING_MANIFEST_REL, target[1])
            elif isinstance(target, tuple) and target[0] == "fixture":
                mutate_json_path(root, STRING_FIXTURE_REL, target[1])
            elif isinstance(target, tuple) and target[0] == "invalid_json":
                (root / target[1]).write_text("{\n", encoding="utf-8")
            else:
                (root / target[1]).unlink()

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

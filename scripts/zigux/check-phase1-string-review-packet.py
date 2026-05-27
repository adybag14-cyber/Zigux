#!/usr/bin/env python3
"""Guard the Phase 1 string helper review packet against helper, manifest, fixture, and lane-note drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
STRING_FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
STRING_LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


EXPECTED_STRING_SOURCE_SYMBOLS = [
    "pub fn memparse(text: []const u8) MemparseResult {",
    "pub fn strlcat(dest: []u8, src: []const u8) usize {",
    "pub fn strscpy(dest: []u8, src: []const u8) isize {",
    "pub fn strscpyPad(dest: []u8, src: []const u8) isize {",
    "pub fn strscpy_pad(dest: []u8, src: []const u8) isize {",
    "pub fn memcpyAndPad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn memcpy_and_pad(dest: []u8, src: []const u8, count: usize, pad: u8) void {",
    "pub fn strtomem(dest: []u8, src: []const u8) void {",
    "pub fn strtomem_pad(dest: []u8, src: []const u8, pad: u8) void {",
    "pub fn memtostr(dest: []u8, src: []const u8) void {",
    "pub fn memtostrPad(dest: []u8, src: []const u8) void {",
    "pub fn memtostr_pad(dest: []u8, src: []const u8) void {",
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
    "pub fn strcmp(lhs: []const u8, rhs: []const u8) i32 {",
    "pub fn strncmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {",
    "pub fn strcasecmp(lhs: []const u8, rhs: []const u8) i32 {",
    "pub fn strncasecmp(lhs: []const u8, rhs: []const u8, count: usize) i32 {",
    "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {",
    "pub fn strspn(buf: []const u8, accept: []const u8) usize {",
    "pub fn strcspn(buf: []const u8, reject: []const u8) usize {",
    "pub fn strstr(buf: []const u8, needle: []const u8) ?usize {",
    "pub fn strnstr(buf: []const u8, needle: []const u8, count: usize) ?usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strlen(buf: []const u8) usize {",
    "pub fn strnlen(buf: []const u8, count: usize) usize {",
    "pub fn strnchrNul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strnchrnul(buf: []const u8, count: usize, needle: u8) usize {",
    "pub fn strchrNul(buf: []const u8, needle: u8) usize {",
    "pub fn strchrnul(buf: []const u8, needle: u8) usize {",
]


EXPECTED_HELPER_TEST_ANCHORS = [
    'test "strtobool accepts common Linux forms"',
    'test "strlcpy copies and returns the source length"',
    'test "strlcat appends within the destination size and reports the attempted length"',
    'test "strlcat truncates with a terminator and keeps the full attempted length"',
    'test "strlcat treats an unterminated destination as full"',
    'test "strlcat handles a zero-length destination buffer"',
    'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
    'test "strscpyPad zero-pads the tail after a short source"',
    'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
    'test "strscpyPad preserves strscpy truncation semantics"',
    'test "strscpy_pad mirrors strscpyPad padding semantics"',
    'test "strscpy and strscpyPad keep one-byte destinations terminated"',
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "memcpy_and_pad mirrors memcpyAndPad padding semantics"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostr stops at embedded NUL without padding the tail"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
    'test "memtostr helpers keep one-byte destinations terminated"',
    'test "streq matches C-string equality semantics"',
    'test "skip trim remove and replace spaces work in place"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    'test "strreplace mirrors replaceChar C-string semantics"',
    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
    'test "strHasSuffix returns the matched suffix length with C-string semantics"',
    'test "strstarts mirrors the header-level prefix helper"',
    'test "strEndsWith honors C-string boundaries"',
    'test "prefix and suffix Linux-style aliases mirror the primary helpers"',
    'test "kbasename returns the final path component with C-string semantics"',
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    'test "matchString finds C-string matches and preserves first-match order"',
    'test "match_string mirrors matchString for empty and matched lists"',
    'test "strcmp mirrors C-string lexical ordering"',
    'test "strcmp stops at embedded NULs and length mismatches"',
    'test "strncmp honors the count limit before later mismatches"',
    'test "strncmp stops at embedded NULs and shorter prefixes"',
    'test "strcasecmp ignores ASCII case and preserves lexical ordering"',
    'test "strcasecmp stops at embedded NULs and length mismatches"',
    'test "strncasecmp honors the count limit before later mismatches"',
    'test "strncasecmp stops at embedded NULs and shorter prefixes"',
    'test "strstr mirrors full-length C-string substring searches"',
    'test "strnstr honors count and C-string boundaries"',
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
    'test "strlen honors C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
    'test "strchrNul and strchrnul return the first match or terminator boundary"',
]

EXPECTED_HELPER_SOURCE_EQUIVALENT_ANCHORS = {
    'test "strlcat appends within the destination size and reports the attempted length"': (
        'test "strlcat appends only the C-string prefix from embedded-NUL sources"'
    ),
}

EXPECTED_HELPER_LOCAL_ONLY_ANCHORS = [
    'test "memchrInv keeps non-zero scans stable across the fast-path cutoff"',
    'test "memchrInv finds a dirty byte in the unaligned prefix before the word fast path"',
    'test "memchrInv keeps aligned word hits stable after consuming an unaligned prefix"',
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
    "memparse_review_summary": "helper-local memparse safety anchors stay explicit through the direct string tests so sign-prefixed invalid input preserves rest, signed inputs keep their trailing-rest split aligned with unsigned parsing, implicit and explicit signed overflow clamp instead of trapping, and suffixes are still consumed after saturation",
    "strlcat_review_anchors": [
        'test "strlcat appends within the destination size and reports the attempted length"',
        'test "strlcat truncates with a terminator and keeps the full attempted length"',
        'test "strlcat treats an unterminated destination as full"',
        'test "strlcat handles a zero-length destination buffer"',
    ],
    "strlcat_review_summary": "helper-local strlcat truncation and destination-boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strlcat() fixture keys, so append length reporting, truncation with a preserved terminator slot, unterminated-destination handling, and zero-length destination behavior remain review-visible at the helper surface",
    "copy_fill_review_anchors": [
        'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
        'test "memcpy_and_pad mirrors memcpyAndPad padding semantics"',
        'test "strtomem copies a C-string prefix without adding a terminator or padding"',
        'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
    ],
    "copy_fill_review_summary": "helper-local raw-copy and pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memcpyAndPad(), memcpy_and_pad(), strtomem(), or strtomem_pad() fixture keys, so prefix-copy, first-NUL stop, alias parity, and caller-selected pad behavior remain review-visible at the helper surface",
    "memtostr_review_anchors": [
        'test "memtostr copies a bounded non-NUL source and adds one terminator"',
        'test "memtostr stops at embedded NUL without padding the tail"',
        'test "memtostrPad zero-pads the remaining tail after copying"',
        'test "memtostr helpers keep one-byte destinations terminated"',
    ],
    "memtostr_review_summary": "helper-local memtostr boundary and tail-padding anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys, so bounded source copies, embedded-NUL stops, terminator insertion, and zero-padded destination tails remain review-visible at the helper surface",
    "prefix_suffix_review_anchors": [
        'test "strHasPrefix returns the matched prefix length with C-string semantics"',
        'test "strHasSuffix returns the matched suffix length with C-string semantics"',
        'test "strstarts mirrors the header-level prefix helper"',
        'test "strEndsWith honors C-string boundaries"',
        'test "prefix and suffix Linux-style aliases mirror the primary helpers"',
    ],
    "prefix_suffix_review_summary": "helper-local prefix and suffix boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still focuses on replaceChar and memchrInv parity rather than dedicated prefix or suffix fixture fields, so strHasPrefix and str_has_prefix plus strHasSuffix and str_has_suffix plus strstarts plus strEndsWith and str_ends_with plus strends remain review-visible at the helper surface",
    "lookup_review_anchors": [
        'test "matchString finds C-string matches and preserves first-match order"',
        'test "match_string mirrors matchString for empty and matched lists"',
    ],
    "lookup_review_summary": "helper-local string lookup anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated matchString() or match_string() fixture keys, so C-string list lookup order and the Linux-style alias remain review-visible at the helper surface",
    "sysfs_review_anchors": [
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    ],
    "sysfs_review_summary": "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface",
    "strscpy_review_anchors": [
        'test "strscpy keeps NUL termination and reports truncation with -E2BIG"',
        'test "strscpyPad zero-pads the tail after a short source"',
        'test "strscpyPad stops at embedded NUL and pads the remaining tail"',
        'test "strscpyPad preserves strscpy truncation semantics"',
        'test "strscpy_pad mirrors strscpyPad padding semantics"',
        'test "strscpy and strscpyPad keep one-byte destinations terminated"',
    ],
    "strscpy_review_summary": "helper-local string copy-and-pad anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strscpy() or strscpyPad() fixture keys",
    "strcmp_review_anchors": [
        'test "strcmp mirrors C-string lexical ordering"',
        'test "strcmp stops at embedded NULs and length mismatches"',
    ],
    "strcmp_review_summary": "helper-local lexical-compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcmp() fixture keys, so lexical ordering and embedded-NUL length-mismatch behavior remain review-visible at the helper surface",
    "casecmp_review_anchors": [
        'test "strcasecmp ignores ASCII case and preserves lexical ordering"',
        'test "strcasecmp stops at embedded NULs and length mismatches"',
        'test "strncasecmp honors the count limit before later mismatches"',
        'test "strncasecmp stops at embedded NULs and shorter prefixes"',
    ],
    "casecmp_review_summary": "helper-local ASCII case-folded compare anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strcasecmp() or strncasecmp() fixture keys, so case-insensitive lexical ordering, embedded-NUL boundaries, and counted-prefix behavior remain review-visible at the helper surface",
    "substring_search_review_anchors": [
        'test "strstr mirrors full-length C-string substring searches"',
        'test "strnstr honors count and C-string boundaries"',
    ],
    "substring_search_review_summary": "helper-local substring-search anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated strstr() or strnstr() fixture keys, so full-length and count-clamped substring boundaries remain review-visible at the helper surface",
    "search_length_review_anchors": [
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strchr and strrchr return the terminator index when searching for NUL"',
        'test "strlen honors C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strchrNul and strchrnul return the first match or terminator boundary"',
    ],
    "search_length_review_summary": "helper-local search-and-length boundary anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated search-length fixture keys, so strchr() or strrchr() boundary scans, terminator-index searches, strchrNul() or strchrnul() match-or-terminator boundaries, and strlen() or strnlen() length boundaries remain review-visible at the helper surface",
    "strnchr_review_anchor": 'test "strnchr honors count and C-string boundaries"',
    "counted_search_review_anchors": [
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strpbrk finds the first accepted byte with C-string semantics"',
        'test "strspn counts the accepted prefix with C-string semantics"',
        'test "strcspn counts until the first rejected byte with C-string semantics"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
        'test "strchrNul and strchrnul return the first match or terminator boundary"',
    ],
    "strnchrnul_review_anchor": 'test "strnchrNul returns the first match, NUL, or count boundary"',
    "strchrnul_review_anchor": 'test "strchrNul and strchrnul return the first match or terminator boundary"',
    "strnchr_review_summary": "the direct counted-search and C-string search-length follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, strnlen() count-clamped length, strnchrNul() or strnchrnul() match-or-NUL boundary behavior, and strchrNul() or strchrnul() match-or-terminator boundaries remain owned by the helper-local anchors",
    "basename_review_anchor": 'test "kbasename returns the final path component with C-string semantics"',
    "basename_review_summary": "helper-local basename path-tail anchor stays explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated kbasename fixture keys, so final path-component extraction at the first C-string terminator remains review-visible at the helper surface",
    "trim_nul_review_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "trim_nul_review_summary": "the direct trim follow-up stays explicit because the shared Phase 1 string fixture records the trimmed bytes but not the preserved tail bytes beyond the first embedded terminator",
    "phase1_trim_cstr_replay_anchor": 'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    "phase1_trim_cstr_replay_summary": "the shared Phase 1 string replay still only locks the plain trailing-whitespace trimSpaces bytes from the committed fixture, while the direct helper-local trim follow-up keeps embedded-NUL trimming for trimSpaces and strim plus strstrip and preserved tail-byte review explicit because the shared packet still does not exercise every trim alias or every post-NUL byte position",
    "memchr_moving_dirty_anchor": 'test "memchrInv follows the earliest dirty byte as long buffers change"',
    "memchr_moving_dirty_review_summary": "the direct memchrInv follow-up stays explicit because the shared Phase 1 fixture pins one fixed dirty index and the clean case, but not the moving earliest-mismatch ownership as later dirty bytes become the next live divergence",
    "phase1_helper_replay_anchor": 'test "strreplace mirrors replaceChar C-string semantics"',
    "shared_replace_char_cstr_review_summary": "the shared Phase 1 string replay now exercises strtobool, strlcpy, skipSpaces, trimSpaces, removeSpaces, replaceChar, and memchrInv fixture parity, while the dedicated embedded-NUL replaceChar follow-up keeps the first-terminator stop rule explicit without widening helper-local memparse ownership",
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
    "next_safe_step_note": "If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, and match-or-terminator review anchors aligned across the string review packet and this lane note unless dedicated shared fixture keys land; do not reopen missing closure-side validator names by default.",
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
        "`PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    ),
    (
        "lane_next_safe_step",
        "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    ),
    (
        "lane_counted_search_match_or_nul",
        "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`."",
    ),
    (
        "lane_counted_search_strspn",
        "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`."",
    ),
]


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json_with_duplicate_tracking(text: str) -> object:
    return json.loads(text, object_pairs_hook=DuplicateTrackingDict)


def load_json(root: Path, relative_path: Path) -> object:
    return load_json_with_duplicate_tracking(load_text(root, relative_path))


def load_json_failure(label: str, exc: json.JSONDecodeError) -> str:
    return f"{label}:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"


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


def require_anchor_occurrence(
    text: str,
    label: str,
    marker: str,
    equivalents: dict[str, str] | None = None,
) -> list[str]:
    equivalents = equivalents or {}
    primary_count = text.count(marker)
    if primary_count == 1:
        return []
    if primary_count == 0 and marker in equivalents:
        equivalent = equivalents[marker]
        equivalent_count = text.count(equivalent)
        if equivalent_count == 1:
            return []
        return [f"{label}:expected=1:actual=0:equivalent_actual={equivalent_count}"]
    return [f"{label}:expected=1:actual={primary_count}"]


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
    duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_manifest_paths:
        return [f"manifest:duplicate_json_key:{path}" for path in duplicate_manifest_paths]

    if not isinstance(fixture, dict):
        return [f"fixture:expected=dict:actual={type(fixture).__name__}"]
    duplicate_fixture_paths = collect_duplicate_json_key_paths(fixture)
    if duplicate_fixture_paths:
        return [f"fixture:duplicate_json_key:{path}" for path in duplicate_fixture_paths]

    for symbol in EXPECTED_STRING_SOURCE_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol))

    seen_helper_anchors: set[str] = set()
    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(
            require_anchor_occurrence(
                helper_text,
                f"string_helper:{anchor}",
                anchor,
                EXPECTED_HELPER_SOURCE_EQUIVALENT_ANCHORS,
            )
        )
        seen_helper_anchors.add(anchor)

    for anchor in EXPECTED_HELPER_LOCAL_ONLY_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"string_helper_local:{anchor}", anchor))
        seen_helper_anchors.add(anchor)

    for key, expected in EXPECTED_STRING_PACKET.items():
        if key == "helper_test_anchors":
            continue
        for anchor in iter_anchor_strings(expected):
            if anchor in seen_helper_anchors:
                continue
            failures.extend(require_exact_occurrence(helper_text, f"string_helper_packet:{key}", anchor))
            seen_helper_anchors.add(anchor)

    for label, marker in EXPECTED_STRING_LANE_MARKERS:
        failures.extend(require_exact_occurrence(lane_text, f"string_lane:{label}", marker))

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
        failures.extend(require_exact_value(f"string_fixture:{key}", string_fixture.get(key), expected))

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_helper_source() -> str:
    lines = EXPECTED_STRING_SOURCE_SYMBOLS + [""] + EXPECTED_HELPER_TEST_ANCHORS + EXPECTED_HELPER_LOCAL_ONLY_ANCHORS
    return "\n".join(lines) + "\n"


def sample_manifest() -> str:
    return json.dumps({"review_anchors": {"tools/lib/string.zig": EXPECTED_STRING_PACKET}}, indent=2) + "\n"


def sample_fixture() -> str:
    return json.dumps({"string": EXPECTED_STRING_FIXTURE_VALUES}, indent=2) + "\n"


def sample_lane_note() -> str:
    return "# sample\n\n" + "\n".join(marker for _, marker in EXPECTED_STRING_LANE_MARKERS) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, sample_helper_source())
    write_file(root, STRING_MANIFEST_REL, sample_manifest())
    write_file(root, STRING_FIXTURE_REL, sample_fixture())
    write_file(root, STRING_LANE_NOTE_REL, sample_lane_note())


def insert_duplicate_json_line(root: Path, relative_path: Path, needle: str, duplicate_line: str) -> None:
    json_path = root / relative_path
    text = json_path.read_text(encoding="utf-8")
    json_path.write_text(text.replace(needle, duplicate_line + "\n" + needle, 1), encoding="utf-8")


def expect_failure_contains(root: Path, prefix: str) -> None:
    failures = collect_failures(root)
    if not any(item.startswith(prefix) for item in failures):
        raise SystemExit(f"phase1-string-review:self-test:{prefix}")


def run_self_test() -> int:
    cases = [
        "missing_file:tools/lib/string.zig",
        'string_helper:test "strlcat appends within the destination size and reports the attempted length":expected=1:actual=0:equivalent_actual=0',
        'string_helper:test "strcasecmp ignores ASCII case and preserves lexical ordering":expected=1:actual=0',
        'string_helper:test "strchrNul and strchrnul return the first match or terminator boundary":expected=1:actual=0',
        'string_helper_local:test "memchrInv keeps non-zero scans stable across the fast-path cutoff":expected=1:actual=0',
        "string_lane:lane_next_safe_step:expected=1:actual=0",
        "string_manifest:review_anchors.tools/lib/string.zig.strlcat_review_summary:expected=",
        "string_manifest:review_anchors.tools/lib/string.zig.casecmp_review_anchors:expected=",
        "string_manifest:review_anchors.tools/lib/string.zig.strchrnul_review_anchor:expected=",
        "string_fixture:replace_char_cstr_end:expected=2:actual=0",
        "manifest:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1",
        "fixture:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1",
        "manifest:duplicate_json_key:review_anchors.tools/lib/string.zig.strlcat_review_anchors",
        "fixture:duplicate_json_key:string.replace_char",
        'string_helper_local:test "memchrInv finds a dirty byte in the unaligned prefix before the word fast path":expected=1:actual=0',
        'string_helper_local:test "memchrInv keeps aligned word hits stable after consuming an unaligned prefix":expected=1:actual=0',
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        if cases[0] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:missing_helper_file")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:baseline")

        helper_path = tmp_root / STRING_HELPER_REL
        lane_path = tmp_root / STRING_LANE_NOTE_REL
        manifest_path = tmp_root / STRING_MANIFEST_REL
        fixture_path = tmp_root / STRING_FIXTURE_REL

        text = helper_path.read_text(encoding="utf-8").replace(
            'test "strlcat appends within the destination size and reports the attempted length"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:strlcat_anchor")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "strlcat appends within the destination size and reports the attempted length"\n',
            'test "strlcat appends only the C-string prefix from embedded-NUL sources"\n',
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:strlcat_source_alias")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "strcasecmp ignores ASCII case and preserves lexical ordering"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[2] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:casecmp_anchor")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "strchrNul and strchrnul return the first match or terminator boundary"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[3] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:strchrnul_anchor")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "memchrInv keeps non-zero scans stable across the fast-path cutoff"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[4] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:memchr_fast_path_anchor")

        build_sample_repo(tmp_root)
        line = EXPECTED_STRING_LANE_MARKERS[1][1]
        lane_path.write_text(lane_path.read_text(encoding="utf-8").replace(line + "\n", "", 1), encoding="utf-8")
        if cases[5] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:lane_next_safe_step")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["strlcat_review_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure_contains(tmp_root, cases[6])

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["casecmp_review_anchors"] = []
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure_contains(tmp_root, cases[7])

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["strchrnul_review_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure_contains(tmp_root, cases[8])

        build_sample_repo(tmp_root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["string"]["replace_char_cstr_end"] = 0
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if cases[9] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:fixture_drift")

        build_sample_repo(tmp_root)
        manifest_path.write_text("{\n", encoding="utf-8")
        if cases[10] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:manifest_invalid_json")

        build_sample_repo(tmp_root)
        fixture_path.write_text("{\n", encoding="utf-8")
        if cases[11] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:fixture_invalid_json")

        build_sample_repo(tmp_root)
        insert_duplicate_json_line(
            tmp_root,
            STRING_MANIFEST_REL,
            '      "strlcat_review_anchors": [',
            '      "strlcat_review_anchors": [],',
        )
        if cases[12] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:manifest_duplicate_json_key")

        build_sample_repo(tmp_root)
        insert_duplicate_json_line(
            tmp_root,
            STRING_FIXTURE_REL,
            '    "replace_char": "a_b",',
            '    "replace_char": "drift",',
        )
        if cases[13] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:fixture_duplicate_json_key")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "memchrInv finds a dirty byte in the unaligned prefix before the word fast path"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[14] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:memchr_unaligned_prefix_anchor")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "memchrInv keeps aligned word hits stable after consuming an unaligned prefix"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[15] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:memchr_aligned_word_hit_anchor")

    print("PHASE1_STRING_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_REVIEW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override the repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
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

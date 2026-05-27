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

EXPECTED_HELPER_LOCAL_ONLY_ANCHORS = [
    'test "memchrInv keeps non-zero scans stable across the fast-path cutoff"',
]

REQUIRED_PACKET_KEYS = [
    "helper_test_anchors",
    "memparse_review_anchors",
    "memparse_review_summary",
    "copy_fill_review_anchors",
    "copy_fill_review_summary",
    "memtostr_review_anchors",
    "memtostr_review_summary",
    "prefix_suffix_review_anchors",
    "prefix_suffix_review_summary",
    "lookup_review_anchors",
    "lookup_review_summary",
    "sysfs_review_anchors",
    "sysfs_review_summary",
    "strscpy_review_anchors",
    "strscpy_review_summary",
    "strcmp_review_anchors",
    "strcmp_review_summary",
    "casecmp_review_anchors",
    "casecmp_review_summary",
    "substring_search_review_anchors",
    "substring_search_review_summary",
    "search_length_review_anchors",
    "search_length_review_summary",
    "counted_search_review_anchors",
    "strnchr_review_summary",
    "basename_review_anchor",
    "basename_review_summary",
    "trim_nul_review_anchor",
    "trim_nul_review_summary",
    "memchr_moving_dirty_anchor",
    "memchr_moving_dirty_review_summary",
    "phase1_helper_replay_anchor",
    "shared_replace_char_cstr_review_summary",
    "parity_fixture_keys",
    "next_safe_step_note",
]

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
        "counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), "
        "strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), "
        "embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-"
        "local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the "
        "current string fixture keys`",
    ),
    (
        "lane_next_safe_step",
        "`PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside "
        "strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix "
        "boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() "
        "C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), "
        "strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and "
        "strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for "
        "committed replaceChar or current string fixture drift; keep the helper-local sysfs review "
        "anchors aligned across the string review packet and this lane note unless dedicated shared "
        "sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
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

SAMPLE_STRING_PACKET = {
    "helper_test_anchors": [
        'test "strtobool accepts common Linux forms"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
        'test "strcasecmp ignores ASCII case and preserves lexical ordering"',
    ],
    "memparse_review_anchors": ['test "strtobool accepts common Linux forms"'],
    "memparse_review_summary": "sample",
    "copy_fill_review_anchors": ['test "strtobool accepts common Linux forms"'],
    "copy_fill_review_summary": "sample",
    "memtostr_review_anchors": ['test "strtobool accepts common Linux forms"'],
    "memtostr_review_summary": "sample",
    "prefix_suffix_review_anchors": ['test "strtobool accepts common Linux forms"'],
    "prefix_suffix_review_summary": "sample",
    "lookup_review_anchors": ['test "sysfsMatchString finds newline-aware matches and preserves first-match order"'],
    "lookup_review_summary": "sample",
    "sysfs_review_anchors": ['test "sysfsMatchString finds newline-aware matches and preserves first-match order"'],
    "sysfs_review_summary": "sample",
    "strscpy_review_anchors": ['test "strtobool accepts common Linux forms"'],
    "strscpy_review_summary": "sample",
    "strcmp_review_anchors": ['test "strtobool accepts common Linux forms"'],
    "strcmp_review_summary": "sample",
    "casecmp_review_anchors": ['test "strcasecmp ignores ASCII case and preserves lexical ordering"'],
    "casecmp_review_summary": "sample",
    "substring_search_review_anchors": ['test "strtobool accepts common Linux forms"'],
    "substring_search_review_summary": "sample",
    "search_length_review_anchors": ['test "strnchrNul returns the first match, NUL, or count boundary"'],
    "search_length_review_summary": "sample",
    "counted_search_review_anchors": ['test "strnchrNul returns the first match, NUL, or count boundary"'],
    "strnchr_review_summary": "sample",
    "basename_review_anchor": 'test "strtobool accepts common Linux forms"',
    "basename_review_summary": "sample",
    "trim_nul_review_anchor": 'test "strtobool accepts common Linux forms"',
    "trim_nul_review_summary": "sample",
    "memchr_moving_dirty_anchor": 'test "strtobool accepts common Linux forms"',
    "memchr_moving_dirty_review_summary": "sample",
    "phase1_helper_replay_anchor": 'test "strtobool accepts common Linux forms"',
    "shared_replace_char_cstr_review_summary": "sample",
    "parity_fixture_keys": list(EXPECTED_STRING_FIXTURE_VALUES.keys()),
    "next_safe_step_note": "sample",
}


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


def collect_test_strings(value: object) -> list[str]:
    anchors: list[str] = []
    if isinstance(value, str):
        if value.startswith('test "'):
            anchors.append(value)
    elif isinstance(value, list):
        for item in value:
            anchors.extend(collect_test_strings(item))
    elif isinstance(value, dict):
        for item in value.values():
            anchors.extend(collect_test_strings(item))
    return anchors


def require_packet_shape(packet: object) -> list[str]:
    failures: list[str] = []
    if not isinstance(packet, dict):
        return [f"string_manifest:packet:expected=dict:actual={type(packet).__name__}"]

    for key in REQUIRED_PACKET_KEYS:
        if key not in packet:
            failures.append(f"string_manifest:missing_key:{key}")
    helper_test_anchors = packet.get("helper_test_anchors")
    if not isinstance(helper_test_anchors, list):
        failures.append("string_manifest:helper_test_anchors:expected=list")
    parity_fixture_keys = packet.get("parity_fixture_keys")
    if not isinstance(parity_fixture_keys, list):
        failures.append("string_manifest:parity_fixture_keys:expected=list")
    return failures


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

    string_packet = nested_value(manifest, ("review_anchors", "tools/lib/string.zig"))
    failures.extend(require_packet_shape(string_packet))
    if failures:
        return failures
    assert isinstance(string_packet, dict)

    helper_test_anchors = string_packet["helper_test_anchors"]
    assert isinstance(helper_test_anchors, list)
    for anchor in helper_test_anchors:
        failures.extend(require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor))

    seen_anchors = set(helper_test_anchors)
    for anchor in EXPECTED_HELPER_LOCAL_ONLY_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"string_helper_local:{anchor}", anchor))
        seen_anchors.add(anchor)

    for anchor in collect_test_strings(string_packet):
        if anchor in seen_anchors:
            continue
        failures.extend(require_exact_occurrence(helper_text, f"string_helper_packet:{anchor}", anchor))
        seen_anchors.add(anchor)

    for label, marker in EXPECTED_STRING_LANE_MARKERS:
        failures.extend(require_exact_occurrence(lane_text, f"string_lane:{label}", marker))

    string_fixture = fixture.get("string")
    if not isinstance(string_fixture, dict):
        return ["string_fixture:expected=dict:actual=missing"]
    for key, expected in EXPECTED_STRING_FIXTURE_VALUES.items():
        failures.extend(require_exact_value(f"string_fixture:{key}", string_fixture.get(key), expected))

    parity_fixture_keys = string_packet.get("parity_fixture_keys")
    if isinstance(parity_fixture_keys, list):
        failures.extend(
            require_exact_value(
                "string_manifest:parity_fixture_keys",
                parity_fixture_keys,
                list(EXPECTED_STRING_FIXTURE_VALUES.keys()),
            )
        )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_helper_source() -> str:
    helper_tests = SAMPLE_STRING_PACKET["helper_test_anchors"]
    extra_tests = EXPECTED_HELPER_LOCAL_ONLY_ANCHORS
    return "\n".join(EXPECTED_STRING_SOURCE_SYMBOLS + [""] + helper_tests + extra_tests) + "\n"


def sample_manifest() -> str:
    return json.dumps({"review_anchors": {"tools/lib/string.zig": SAMPLE_STRING_PACKET}}, indent=2) + "\n"


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


def run_self_test() -> int:
    cases = [
        ("missing_helper_file", "missing_file:tools/lib/string.zig"),
        (
            "missing_source_symbol",
            "string_source:pub fn memparse(text: []const u8) MemparseResult {:expected=1:actual=0",
        ),
        (
            "missing_helper_anchor",
            'string_helper:test "sysfsMatchString finds newline-aware matches and preserves first-match order":expected=1:actual=0',
        ),
        (
            "missing_helper_local_anchor",
            'string_helper_local:test "memchrInv keeps non-zero scans stable across the fast-path cutoff":expected=1:actual=0',
        ),
        (
            "missing_lane_marker",
            "string_lane:lane_direct_owner:expected=1:actual=0",
        ),
        (
            "fixture_drift",
            "string_fixture:replace_char_cstr_end:expected=2:actual=0",
        ),
        (
            "manifest_invalid_json",
            "manifest:invalid_json:Expecting property name enclosed in double quotes:line=2:column=1",
        ),
        (
            "fixture_duplicate_json_key",
            "fixture:duplicate_json_key:string.replace_char",
        ),
        (
            "missing_manifest_key",
            "string_manifest:missing_key:casecmp_review_summary",
        ),
        (
            "parity_fixture_key_drift",
            "string_manifest:parity_fixture_keys:expected=",
        ),
    ]

    with tempfile.TemporaryDirectory(prefix="zigux_phase1_string_review_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        if cases[0][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:missing_helper_file")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:baseline")

        helper_path = tmp_root / STRING_HELPER_REL
        lane_path = tmp_root / STRING_LANE_NOTE_REL
        manifest_path = tmp_root / STRING_MANIFEST_REL
        fixture_path = tmp_root / STRING_FIXTURE_REL

        text = helper_path.read_text(encoding="utf-8").replace(
            "pub fn memparse(text: []const u8) MemparseResult {\n", "", 1
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[1][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:missing_source_symbol")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "sysfsMatchString finds newline-aware matches and preserves first-match order"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[2][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:missing_helper_anchor")

        build_sample_repo(tmp_root)
        text = helper_path.read_text(encoding="utf-8").replace(
            'test "memchrInv keeps non-zero scans stable across the fast-path cutoff"\n',
            "",
            1,
        )
        helper_path.write_text(text, encoding="utf-8")
        if cases[3][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:missing_helper_local_anchor")

        build_sample_repo(tmp_root)
        line = EXPECTED_STRING_LANE_MARKERS[0][1]
        text = lane_path.read_text(encoding="utf-8").replace(line + "\n", "", 1)
        lane_path.write_text(text, encoding="utf-8")
        if cases[4][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:missing_lane_marker")

        build_sample_repo(tmp_root)
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        fixture["string"]["replace_char_cstr_end"] = 0
        fixture_path.write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if not any(item.startswith(cases[5][1]) for item in collect_failures(tmp_root)):
            raise SystemExit("phase1-string-review:self-test:fixture_drift")

        build_sample_repo(tmp_root)
        manifest_path.write_text("{\n", encoding="utf-8")
        if cases[6][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:manifest_invalid_json")

        build_sample_repo(tmp_root)
        insert_duplicate_json_line(
            tmp_root,
            STRING_FIXTURE_REL,
            '    "replace_char": "a_b",',
            '    "replace_char": "drift",',
        )
        if cases[7][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:fixture_duplicate_json_key")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        del manifest["review_anchors"]["tools/lib/string.zig"]["casecmp_review_summary"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if cases[8][1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-review:self-test:missing_manifest_key")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["parity_fixture_keys"] = ["drift"]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not any(item.startswith(cases[9][1]) for item in collect_failures(tmp_root)):
            raise SystemExit("phase1-string-review:self-test:parity_fixture_key_drift")

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
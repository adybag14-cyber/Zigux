#!/usr/bin/env python3
"""Guard the current Phase 1 string closure packet against helper and reminder drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parent
HELPER_REL = Path("tools/lib/string.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
FIXTURE_REL = Path("zigux/tests/fixtures/phase1_helpers.json")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
CLOSURE_NOTE_REL = Path("Documentation/zigux/phase1-closure.md")
VALIDATOR_REL = Path("scripts/zigux/validate-phase1-closure.py")
REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")

HELPER_MARKERS = [
    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
    'test "phase 1 string trim helpers stop at embedded NUL after trailing whitespace"',
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "matchString finds C-string matches and preserves first-match order"',
    'test "strcmp mirrors C-string lexical ordering"',
    'test "memchrInv follows the earliest dirty byte as long buffers change"',
    'test "memparse saturates signed overflow instead of trapping"',
    'test "strspn counts the accepted prefix with C-string semantics"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
]

LANE_LINES = [
    "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
    "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.",
    "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`.",
]

CLOSURE_MARKERS = {
    "string_sysfs_review": "`PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
    "string_memtostr_review": "Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors. Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements until dedicated fixture keys land.",
    "string_tie_breaker": "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local `strscpy()` or `strscpyPad()` copy-and-pad anchors, memparse safety anchors, matched-prefix-length or suffix-boundary anchors, sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, C-string list lookup anchors through `matchString()` and `match_string()`, lexical-compare and search-or-length boundary anchors through `strcmp()`, `strlen()`, `strnlen()`, `strchr()`, `strrchr()`, `strchrNul()`, and `strchrnul()`, counted-search anchors through `strpbrk()`, `strcspn()`, `strnchr()`, `strnchrNul()` or `strnchrnul()`, and `strspn()`, embedded-NUL trim preservation, or moving-earliest-dirty-byte `memchrInv()` coverage, or unless committed `replaceChar` parity bytes or current string fixture keys drift; do not reopen missing closure-side validator names by default. Current `master` still keeps that broader string review packet explicit in `tools/lib/string.zig`, the committed manifest, `scripts/zigux/check-phase1-string-review-packet.py`, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless those direct string review surfaces drift, committed `replaceChar` parity bytes drift, or dedicated shared string fixture keys land.",
}

VALIDATOR_MARKERS = [
    'STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")',
    'STRING_HELPER_REL = Path("tools/lib/string.zig")',
    '"string_sysfs_review":',
    '"string_memtostr_review":',
    '("review_anchors", "tools/lib/string.zig", "next_safe_step_note")',
    '(STRING_REVIEW_CHECKER_REL, "phase1-string-review-packet"),',
]

REVIEW_CHECKER_MARKERS = [
    "EXPECTED_STRING_PACKET = {",
    "EXPECTED_STRING_FIXTURE_VALUES = {",
    "EXPECTED_STRING_LANE_MARKERS = [",
    "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface",
    "helper-local memtostr boundary and tail-padding anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys, so bounded source copies, embedded-NUL stops, terminator insertion, and zero-padded destination tails remain review-visible at the helper surface",
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.",
]

MANIFEST_EXPECTATIONS = {
    ("lane_sequencing", "direct_anchor_followup_helpers"): [
        "tools/lib/bitmap.zig",
        "tools/lib/find_bit.zig",
        "tools/lib/rbtree.zig",
        "tools/lib/string.zig",
    ],
    ("review_anchors", "tools/lib/string.zig", "sysfs_review_anchors"): [
        'test "sysfsStreq treats trailing newline and NUL as equivalent"',
        'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
        'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
        'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    ],
    ("review_anchors", "tools/lib/string.zig", "sysfs_review_summary"): "helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface",
    ("review_anchors", "tools/lib/string.zig", "memtostr_review_anchors"): [
        'test "memtostr copies a bounded non-NUL source and adds one terminator"',
        'test "memtostr stops at embedded NUL without padding the tail"',
        'test "memtostrPad zero-pads the remaining tail after copying"',
        'test "memtostr helpers keep one-byte destinations terminated"',
    ],
    ("review_anchors", "tools/lib/string.zig", "memtostr_review_summary"): "helper-local memtostr boundary and tail-padding anchors stay explicit through the direct string tests because the shared Phase 1 replay still does not carry dedicated memtostr(), memtostrPad(), or memtostr_pad() fixture keys, so bounded source copies, embedded-NUL stops, terminator insertion, and zero-padded destination tails remain review-visible at the helper surface",
    ("review_anchors", "tools/lib/string.zig", "memparse_review_anchors"): [
        'test "memparse handles decimal hexadecimal octal and suffixes"',
        'test "memparse keeps original rest when sign is not followed by digits"',
        'test "memparse saturates signed overflow instead of trapping"',
        'test "memparse clamps explicit positive signed overflow"',
        'test "memparse keeps signed values and their trailing rest aligned"',
        'test "memparse consumes suffix after saturation"',
        'test "memparse applies suffixes before signed clamping"',
    ],
    ("review_anchors", "tools/lib/string.zig", "counted_search_review_anchors"): [
        'test "strchr mirrors full-length C-string searches"',
        'test "strrchr finds the last in-range match with C-string semantics"',
        'test "strpbrk finds the first accepted byte with C-string semantics"',
        'test "strspn counts the accepted prefix with C-string semantics"',
        'test "strcspn counts until the first rejected byte with C-string semantics"',
        'test "strnchr honors count and C-string boundaries"',
        'test "strnlen honors count and C-string boundaries"',
        'test "strnchrNul returns the first match, NUL, or count boundary"',
    ],
    ("review_anchors", "tools/lib/string.zig", "strnchrnul_review_anchor"): 'test "strnchrNul returns the first match, NUL, or count boundary"',
    ("review_anchors", "tools/lib/string.zig", "strnchr_review_summary"): "the direct counted-search and C-string search-length follow-up stays explicit because the shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() count-limited scanning, strnlen() count-clamped length, and strnchrNul() or strnchrnul() match-or-NUL boundary behavior remain owned by the helper-local anchors",
    ("review_anchors", "tools/lib/string.zig", "parity_fixture_keys"): [
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
    ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"): "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default.",
}

FIXTURE_EXPECTATIONS = {
    ("string", "strtobool_y"): True,
    ("string", "strtobool_on"): True,
    ("string", "strlcpy_len"): 5,
    ("string", "skip_spaces"): "hello",
    ("string", "trim_spaces"): "hi",
    ("string", "replace_char"): "a_b",
    ("string", "replace_char_end"): 3,
    ("string", "replace_char_cstr_end"): 2,
    ("string", "replace_char_cstr_bytes"): [97, 95, 0, 45, 122],
    ("string", "memchr_inv_index"): 4,
    ("string", "memchr_inv_none"): True,
}


class DuplicateTrackingDict(dict[str, object]):
    def __init__(self, pairs: list[tuple[str, object]]) -> None:
        super().__init__()
        self.duplicate_keys: list[str] = []
        for key, value in pairs:
            if key in self and key not in self.duplicate_keys:
                self.duplicate_keys.append(key)
            self[key] = value


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def read_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(read_text(root, relative_path), object_pairs_hook=DuplicateTrackingDict)


def duplicate_paths(data: object, prefix: tuple[str, ...] = ()) -> list[str]:
    paths: list[str] = []
    if isinstance(data, DuplicateTrackingDict):
        for key in data.duplicate_keys:
            paths.append(".".join(prefix + (key,)))
    if isinstance(data, dict):
        for key, value in data.items():
            paths.extend(duplicate_paths(value, prefix + (key,)))
    elif isinstance(data, list):
        for value in data:
            paths.extend(duplicate_paths(value, prefix))
    return paths


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def exact_count(text: str, needle: str) -> int:
    return text.count(needle)


def exact_line_count(text: str, needle: str) -> int:
    want = needle.strip()
    return sum(1 for line in text.splitlines() if line.strip() == want)


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    required = (
        HELPER_REL,
        MANIFEST_REL,
        FIXTURE_REL,
        LANE_NOTE_REL,
        CLOSURE_NOTE_REL,
        VALIDATOR_REL,
        REVIEW_CHECKER_REL,
    )
    for relative_path in required:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = read_text(root, HELPER_REL)
    lane_text = read_text(root, LANE_NOTE_REL)
    closure_text = read_text(root, CLOSURE_NOTE_REL)
    validator_text = read_text(root, VALIDATOR_REL)
    review_checker_text = read_text(root, REVIEW_CHECKER_REL)

    for marker in HELPER_MARKERS:
        count = exact_count(helper_text, marker)
        if count != 1:
            failures.append(f"helper:{marker}:expected=1:actual={count}")
    for line in LANE_LINES:
        count = exact_line_count(lane_text, line)
        if count != 1:
            failures.append(f"lane:{line}:expected=1:actual={count}")
    for label, marker in CLOSURE_MARKERS.items():
        count = exact_count(closure_text, marker)
        if count != 1:
            failures.append(f"closure:{label}:expected=1:actual={count}")
    for marker in VALIDATOR_MARKERS:
        count = exact_count(validator_text, marker)
        if count != 1:
            failures.append(f"validator:{marker}:expected=1:actual={count}")
    for marker in REVIEW_CHECKER_MARKERS:
        count = exact_count(review_checker_text, marker)
        if count != 1:
            failures.append(f"review_checker:{marker}:expected=1:actual={count}")

    try:
        manifest = load_json(root, MANIFEST_REL)
    except json.JSONDecodeError as exc:
        return [f"manifest:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    dup_manifest = duplicate_paths(manifest)
    if dup_manifest:
        return [f"manifest:duplicate_json_key:{path}" for path in dup_manifest]
    for path, expected in MANIFEST_EXPECTATIONS.items():
        actual = nested_value(manifest, path)
        if actual != expected:
            failures.append(f"manifest:{'.'.join(path)}")

    try:
        fixture = load_json(root, FIXTURE_REL)
    except json.JSONDecodeError as exc:
        return [f"fixture:invalid_json:{exc.msg}:line={exc.lineno}:column={exc.colno}"]
    dup_fixture = duplicate_paths(fixture)
    if dup_fixture:
        return [f"fixture:duplicate_json_key:{path}" for path in dup_fixture]
    for path, expected in FIXTURE_EXPECTATIONS.items():
        actual = nested_value(fixture, path)
        if actual != expected:
            failures.append(f"fixture:{'.'.join(path)}")

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(root, HELPER_REL, "\n".join(HELPER_MARKERS) + "\n")

    manifest: dict[str, object] = {"lane_sequencing": {}, "review_anchors": {"tools/lib/string.zig": {}}}
    for path, value in MANIFEST_EXPECTATIONS.items():
        current = manifest
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, MANIFEST_REL, json.dumps(manifest, indent=2) + "\n")

    fixture: dict[str, object] = {"string": {}}
    for path, value in FIXTURE_EXPECTATIONS.items():
        current = fixture
        for key in path[:-1]:
            current = current.setdefault(key, {})  # type: ignore[assignment]
        current[path[-1]] = value
    write_file(root, FIXTURE_REL, json.dumps(fixture, indent=2) + "\n")

    write_file(root, LANE_NOTE_REL, "# sample\n\n" + "\n".join(LANE_LINES) + "\n")
    write_file(root, CLOSURE_NOTE_REL, "# sample\n\n" + "\n".join(CLOSURE_MARKERS.values()) + "\n")
    write_file(root, VALIDATOR_REL, "\n".join(VALIDATOR_MARKERS) + "\n")
    write_file(root, REVIEW_CHECKER_REL, "\n".join(REVIEW_CHECKER_MARKERS) + "\n")


def run_self_test() -> int:
    cases = [
        "baseline",
        "missing_helper_marker",
        "missing_lane_line",
        "missing_closure_marker",
        "missing_validator_marker",
        "missing_review_checker_marker",
        "manifest_drift",
        "fixture_drift",
        "manifest_duplicate_key",
        "fixture_invalid_json",
    ]

    with tempfile.TemporaryDirectory(prefix="phase1-string-closure-packet-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        if collect_failures(root):
            print("PHASE1_STRING_CLOSURE_PACKET_SELF_TEST=fail")
            return 1

        (root / HELPER_REL).write_text("\n".join(HELPER_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_helper_marker:expected_failure")
            return 1

        build_sample_repo(root)
        (root / LANE_NOTE_REL).write_text("# sample\n\n" + "\n".join(LANE_LINES[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_lane_line:expected_failure")
            return 1

        build_sampleRepo = build_sample_repo
        build_sampleRepo(root)
        (root / CLOSURE_NOTE_REL).write_text("# sample\n\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_closure_marker:expected_failure")
            return 1

        build_sample_repo(root)
        (root / VALIDATOR_REL).write_text("\n".join(VALIDATOR_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_validator_marker:expected_failure")
            return 1

        build_sample_repo(root)
        (root / REVIEW_CHECKER_REL).write_text("\n".join(REVIEW_CHECKER_MARKERS[1:]) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:missing_review_checker_marker:expected_failure")
            return 1

        build_sample_repo(root)
        manifest = json.loads((root / MANIFEST_REL).read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["strnchrnul_review_anchor"] = "drift"
        (root / MANIFEST_REL).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:manifest_drift:expected_failure")
            return 1

        build_sample_repo(root)
        fixture = json.loads((root / FIXTURE_REL).read_text(encoding="utf-8"))
        fixture["string"]["replace_char_cstr_end"] = 0
        (root / FIXTURE_REL).write_text(json.dumps(fixture, indent=2) + "\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:fixture_drift:expected_failure")
            return 1

        build_sample_repo(root)
        manifest_text = (root / MANIFEST_REL).read_text(encoding="utf-8")
        (root / MANIFEST_REL).write_text(
            manifest_text.replace(
                '      "strnchrnul_review_anchor": "test \\"strnchrNul returns the first match, NUL, or count boundary\\"",',
                '      "strnchrnul_review_anchor": "drift",\n      "strnchrnul_review_anchor": "test \\"strnchrNul returns the first match, NUL, or count boundary\\"",',
                1,
            ),
            encoding="utf-8",
        )
        if not collect_failures(root):
            print("self-test:manifest_duplicate_key:expected_failure")
            return 1

        build_sample_repo(root)
        (root / FIXTURE_REL).write_text("{\n", encoding="utf-8")
        if not collect_failures(root):
            print("self-test:fixture_invalid_json:expected_failure")
            return 1

    print("PHASE1_STRING_CLOSURE_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_CLOSURE_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument(
        "--write-sample-root",
        help="write a sample marker-faithful repo root for focused replay",
    )
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.write_sample_root:
        build_sample_repo(Path(args.write_sample_root).resolve())
        print(f"PHASE1_STRING_CLOSURE_PACKET_SAMPLE_ROOT={Path(args.write_sample_root).resolve()}")
        return 0

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_STRING_CLOSURE_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_STRING_CLOSURE_PACKET=pass")
    print(f"PHASE1_STRING_CLOSURE_PACKET_HELPER={HELPER_REL.as_posix()}")
    print(f"PHASE1_STRING_CLOSURE_PACKET_MANIFEST={MANIFEST_REL.as_posix()}")
    print(f"PHASE1_STRING_CLOSURE_PACKET_FIXTURE={FIXTURE_REL.as_posix()}")
    print(f"PHASE1_STRING_CLOSURE_PACKET_LANE_NOTE={LANE_NOTE_REL.as_posix()}")
    print(f"PHASE1_STRING_CLOSURE_PACKET_CLOSURE_NOTE={CLOSURE_NOTE_REL.as_posix()}")
    print(f"PHASE1_STRING_CLOSURE_PACKET_VALIDATOR={VALIDATOR_REL.as_posix()}")
    print(f"PHASE1_STRING_CLOSURE_PACKET_REVIEW_CHECKER={REVIEW_CHECKER_REL.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
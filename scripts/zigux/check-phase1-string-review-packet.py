#!/usr/bin/env python3
"""Guard the Phase 1 string helper review anchors against direct helper drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent
STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

EXPECTED_STRING_SOURCE_SYMBOLS = [
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn matchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn strnchr(buf: []const u8, count: usize, needle: u8) ?usize {",
    "pub fn strnlen(buf: []const u8, count: usize) usize {",
    "pub fn strchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strrchr(buf: []const u8, needle: u8) ?usize {",
    "pub fn strpbrk(buf: []const u8, accept: []const u8) ?usize {",
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
    'test "strpbrk finds the first accepted byte with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
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

EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS = [
    'test "strHasPrefix returns the matched prefix length with C-string semantics"',
    'test "strHasSuffix returns the matched suffix length with C-string semantics"',
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

EXPECTED_COUNTED_SEARCH_REVIEW_ANCHORS = [
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strpbrk finds the first accepted byte with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
]

EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY = (
    "helper-local prefix and suffix boundary anchors stay explicit through the direct "
    "string tests because the shared Phase 1 replay still focuses on replaceChar and "
    "memchrInv parity rather than dedicated prefix or suffix fixture fields, so "
    "strHasPrefix and str_has_prefix plus strHasSuffix and str_has_suffix plus "
    "strstarts plus strEndsWith and str_ends_with plus strends remain review-visible "
    "at the helper surface"
)

EXPECTED_LOOKUP_REVIEW_SUMMARY = (
    "helper-local string lookup anchors stay explicit through the direct string tests "
    "because the shared Phase 1 replay still does not carry dedicated matchString() "
    "or match_string() fixture keys, so C-string list lookup order and the Linux-style "
    "alias remain review-visible at the helper surface"
)

EXPECTED_SYSFS_REVIEW_SUMMARY = (
    "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit "
    "through the direct string tests because the shared Phase 1 replay still carries "
    "no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus "
    "sysfsMatchString and sysfs_match_string remain review-visible at the helper surface"
)

EXPECTED_STRNCHR_REVIEW_SUMMARY = (
    "the direct counted-search and C-string search-length follow-up stays explicit "
    "because the shared Phase 1 replay still does not carry dedicated counted-search "
    "or search-length fixture keys, so strchr() or strrchr() full-length C-string "
    "searches, strpbrk() first-accepted-byte scanning, strnchr() count-limited "
    "scanning, strnlen() count-clamped length, and strnchrNul() or strnchrnul() "
    "match-or-NUL boundary behavior remain owned by the helper-local anchors"
)

EXPECTED_MEMPARSE_REVIEW_SUMMARY = (
    "helper-local memparse safety anchors stay explicit through the direct string tests "
    "so sign-prefixed invalid input preserves rest, signed inputs keep their "
    "trailing-rest split aligned with unsigned parsing, implicit and explicit signed "
    "overflow clamp instead of trapping, and suffixes are still consumed after saturation"
)

EXPECTED_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned "
    "across the string review packet and this lane note unless dedicated shared sysfs "
    "fixture keys land; do not reopen missing closure-side validator names by default."
)

MANIFEST_EXPECTATIONS = {
    ("review_anchors", "tools/lib/string.zig", "memparse_review_anchors"): EXPECTED_MEMPARSE_REVIEW_ANCHORS,
    ("review_anchors", "tools/lib/string.zig", "prefix_suffix_review_anchors"): EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS,
    ("review_anchors", "tools/lib/string.zig", "lookup_review_anchors"): EXPECTED_LOOKUP_REVIEW_ANCHORS,
    ("review_anchors", "tools/lib/string.zig", "sysfs_review_anchors"): EXPECTED_SYSFS_REVIEW_ANCHORS,
    ("review_anchors", "tools/lib/string.zig", "counted_search_review_anchors"): EXPECTED_COUNTED_SEARCH_REVIEW_ANCHORS,
    ("review_anchors", "tools/lib/string.zig", "strnchr_review_anchor"): 'test "strnchr honors count and C-string boundaries"',
    ("review_anchors", "tools/lib/string.zig", "strnchrnul_review_anchor"): 'test "strnchrNul returns the first match, NUL, or count boundary"',
    ("review_anchors", "tools/lib/string.zig", "prefix_suffix_review_summary"): EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY,
    ("review_anchors", "tools/lib/string.zig", "lookup_review_summary"): EXPECTED_LOOKUP_REVIEW_SUMMARY,
    ("review_anchors", "tools/lib/string.zig", "sysfs_review_summary"): EXPECTED_SYSFS_REVIEW_SUMMARY,
    ("review_anchors", "tools/lib/string.zig", "strnchr_review_summary"): EXPECTED_STRNCHR_REVIEW_SUMMARY,
    ("review_anchors", "tools/lib/string.zig", "memparse_review_summary"): EXPECTED_MEMPARSE_REVIEW_SUMMARY,
    ("review_anchors", "tools/lib/string.zig", "next_safe_step_note"): EXPECTED_NEXT_SAFE_STEP_NOTE,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


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


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []

    for relative_path in (STRING_HELPER_REL, STRING_MANIFEST_REL):
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    manifest = load_json(root, STRING_MANIFEST_REL)
    if not isinstance(manifest, dict):
        return [f"manifest:expected=dict:actual={type(manifest).__name__}"]

    for symbol in EXPECTED_STRING_SOURCE_SYMBOLS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_source:{symbol}", symbol)
        )

    for anchor in EXPECTED_HELPER_TEST_ANCHORS:
        failures.extend(
            require_exact_occurrence(helper_text, f"string_helper:{anchor}", anchor)
        )

    for path, expected in MANIFEST_EXPECTATIONS.items():
        failures.extend(
            require_exact_value(
                f"string_manifest:{'.'.join(path)}",
                nested_value(manifest, path),
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
                    "tools/lib/string.zig": {
                        "memparse_review_anchors": EXPECTED_MEMPARSE_REVIEW_ANCHORS,
                        "prefix_suffix_review_anchors": EXPECTED_PREFIX_SUFFIX_REVIEW_ANCHORS,
                        "lookup_review_anchors": EXPECTED_LOOKUP_REVIEW_ANCHORS,
                        "sysfs_review_anchors": EXPECTED_SYSFS_REVIEW_ANCHORS,
                        "counted_search_review_anchors": EXPECTED_COUNTED_SEARCH_REVIEW_ANCHORS,
                        "strnchr_review_anchor": 'test "strnchr honors count and C-string boundaries"',
                        "strnchrnul_review_anchor": 'test "strnchrNul returns the first match, NUL, or count boundary"',
                        "prefix_suffix_review_summary": EXPECTED_PREFIX_SUFFIX_REVIEW_SUMMARY,
                        "lookup_review_summary": EXPECTED_LOOKUP_REVIEW_SUMMARY,
                        "sysfs_review_summary": EXPECTED_SYSFS_REVIEW_SUMMARY,
                        "strnchr_review_summary": EXPECTED_STRNCHR_REVIEW_SUMMARY,
                        "memparse_review_summary": EXPECTED_MEMPARSE_REVIEW_SUMMARY,
                        "next_safe_step_note": EXPECTED_NEXT_SAFE_STEP_NOTE,
                    }
                }
            },
            indent=2,
        )
        + "\n"
    )


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        STRING_HELPER_REL,
        "\n".join(EXPECTED_STRING_SOURCE_SYMBOLS + EXPECTED_HELPER_TEST_ANCHORS) + "\n",
    )
    write_file(root, STRING_MANIFEST_REL, sample_manifest())


def mutate_manifest(root: Path, path: tuple[str, ...]) -> None:
    manifest_path = root / STRING_MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current = manifest
    for key in path[:-1]:
        current = current[key]
    final_key = path[-1]
    value = current[final_key]
    if isinstance(value, list):
        current[final_key] = value[1:]
    else:
        current[final_key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


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
            f"manifest_{'_'.join(path).replace('.', '_')}",
            ("manifest", path),
            "manifest",
        )
        for path in MANIFEST_EXPECTATIONS
    )
    mutation_specs.append(("manifest_missing_file", ("manifest_missing_file", STRING_MANIFEST_REL), "missing_file"))

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
            elif isinstance(target, tuple) and target[0] == "manifest":
                mutate_manifest(root, target[1])
            else:
                (root / STRING_MANIFEST_REL).unlink()

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

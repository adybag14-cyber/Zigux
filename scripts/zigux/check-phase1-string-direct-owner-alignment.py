#!/usr/bin/env python3
"""Guard the Phase 1 string direct-owner packet against manifest, checker, lane-note, and helper drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

STRING_HELPER_REL = Path("tools/lib/string.zig")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")

REQUIRED_FILES = (
    STRING_HELPER_REL,
    MANIFEST_REL,
    STRING_REVIEW_CHECKER_REL,
    LANE_NOTE_REL,
)

EXPECTED_COPY_FILL_ANCHORS = [
    'test "memcpyAndPad copies the requested prefix and pads the destination tail"',
    'test "memcpy_and_pad mirrors memcpyAndPad padding semantics"',
    'test "strtomem copies a C-string prefix without adding a terminator or padding"',
    'test "strtomem_pad copies through the first NUL and pads the remaining tail"',
]

EXPECTED_MEMTOSTR_ANCHORS = [
    'test "memtostr copies a bounded non-NUL source and adds one terminator"',
    'test "memtostr stops at embedded NUL without padding the tail"',
    'test "memtostrPad zero-pads the remaining tail after copying"',
    'test "memtostr helpers keep one-byte destinations terminated"',
]

EXPECTED_COUNTED_SEARCH_ANCHORS = [
    'test "strchr mirrors full-length C-string searches"',
    'test "strrchr finds the last in-range match with C-string semantics"',
    'test "strpbrk finds the first accepted byte with C-string semantics"',
    'test "strspn counts the accepted prefix with C-string semantics"',
    'test "strcspn counts until the first rejected byte with C-string semantics"',
    'test "strnchr honors count and C-string boundaries"',
    'test "strnlen honors count and C-string boundaries"',
    'test "strnchrNul returns the first match, NUL, or count boundary"',
    'test "strchrNul and strchrnul return the first match or terminator boundary"',
]

EXPECTED_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local strlcat, sysfs, case-insensitive compare, "
    "and match-or-terminator review anchors aligned across the string review packet and this lane "
    "note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side "
    "validator names by default."
)

EXPECTED_COUNTED_SEARCH_REVIEW_SUMMARY = (
    "the direct counted-search and C-string search-length follow-up stays explicit because the "
    "shared Phase 1 replay still does not carry dedicated counted-search or search-length fixture "
    "keys, so strchr() or strrchr() full-length C-string searches, strpbrk() first-accepted-byte "
    "scanning, strspn() accepted-prefix scanning, strcspn() rejected-byte scanning, strnchr() "
    "count-limited scanning, strnlen() count-clamped length, strnchrNul() or strnchrnul() "
    "match-or-NUL boundary behavior, and strchrNul() or strchrnul() match-or-terminator "
    "boundaries remain owned by the helper-local anchors"
)

EXPECTED_LANE_LINES = [
    "- the same string-local packet also keeps helper-local byte-copy and pad coverage explicit through `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, `strtomem_pad()`, `memtostr()`, `memtostrPad()`, and `memtostr_pad()`, with direct tests for requested-prefix copying, first-NUL truncation, terminator insertion, and destination-tail padding, so future string-only rereads should keep those anchors in the same helper-local packet until dedicated shared fixture keys land.",
    "- The counted-search owner term here also covers the current `strnchrNul()` and `strnchrnul()` match-or-NUL boundary anchor already cataloged in `zigux/tests/fixtures/phase1_helper_manifest.json`, so future string-only rereads should keep that helper-local boundary proof inside the same counted-search packet instead of treating it as an unowned follow-up beside `strnchr()`.",
    "- the same counted-search packet now also keeps the direct `strspn()` accepted-prefix anchor review-visible on current `master`, so future string-only rereads should treat accepted-byte-prefix scanning as part of that helper-local search family instead of leaving it implicit beside `strpbrk()` and `strnchr()`.",
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search and search-length anchors through strpbrk(), strspn(), strcspn(), strnchr(), strnchrNul() or strnchrnul(), strchr(), strrchr(), strlen(), and strnlen(), embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
]


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


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path), object_pairs_hook=DuplicateTrackingDict)


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


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def require_exact_occurrence(text: str, label: str, needle: str) -> list[str]:
    count = text.count(needle)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line(text: str, label: str, line: str) -> list[str]:
    want = line.strip()
    count = sum(1 for current in text.splitlines() if current.strip() == want)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_value(label: str, actual: object, expected: object) -> list[str]:
    return [] if actual == expected else [f"{label}:expected={expected!r}:actual={actual!r}"]


def collect_failures(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    checker_text = load_text(root, STRING_REVIEW_CHECKER_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    manifest = load_json(root, MANIFEST_REL)

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    duplicate_manifest_paths = collect_duplicate_json_key_paths(manifest)
    if duplicate_manifest_paths:
        return [f"{MANIFEST_REL.as_posix()}:duplicate_json_key:{path}" for path in duplicate_manifest_paths]

    for anchor in EXPECTED_COPY_FILL_ANCHORS + EXPECTED_MEMTOSTR_ANCHORS + EXPECTED_COUNTED_SEARCH_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper:{anchor}", anchor))
        failures.extend(require_exact_occurrence(checker_text, f"checker:{anchor}", anchor))

    for line in EXPECTED_LANE_LINES:
        failures.extend(require_exact_line(lane_text, f"lane:{line[:48]}", line))

    failures.extend(
        require_exact_value(
            "manifest:copy_fill_review_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "copy_fill_review_anchors")),
            EXPECTED_COPY_FILL_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:memtostr_review_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "memtostr_review_anchors")),
            EXPECTED_MEMTOSTR_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:counted_search_review_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "counted_search_review_anchors")),
            EXPECTED_COUNTED_SEARCH_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:next_safe_step_note",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "next_safe_step_note")),
            EXPECTED_NEXT_SAFE_STEP_NOTE,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:strnchr_review_summary",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "strnchr_review_summary")),
            EXPECTED_COUNTED_SEARCH_REVIEW_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:strchrnul_review_anchor",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "strchrnul_review_anchor")),
            'test "strchrNul and strchrnul return the first match or terminator boundary"',
        )
    )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    destination = root / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    data = {
        "review_anchors": {
            "tools/lib/string.zig": {
                "copy_fill_review_anchors": EXPECTED_COPY_FILL_ANCHORS,
                "memtostr_review_anchors": EXPECTED_MEMTOSTR_ANCHORS,
                "counted_search_review_anchors": EXPECTED_COUNTED_SEARCH_ANCHORS,
                "next_safe_step_note": EXPECTED_NEXT_SAFE_STEP_NOTE,
                "strnchr_review_summary": EXPECTED_COUNTED_SEARCH_REVIEW_SUMMARY,
                "strchrnul_review_anchor": 'test "strchrNul and strchrnul return the first match or terminator boundary"',
            }
        }
    }
    return json.dumps(data, indent=2) + "\n"


def sample_helper() -> str:
    return "\n".join(EXPECTED_COPY_FILL_ANCHORS + EXPECTED_MEMTOSTR_ANCHORS + EXPECTED_COUNTED_SEARCH_ANCHORS) + "\n"


def sample_checker() -> str:
    lines = EXPECTED_COPY_FILL_ANCHORS + EXPECTED_MEMTOSTR_ANCHORS + EXPECTED_COUNTED_SEARCH_ANCHORS
    lines.append(EXPECTED_NEXT_SAFE_STEP_NOTE)
    lines.append(EXPECTED_COUNTED_SEARCH_REVIEW_SUMMARY)
    return "\n".join(lines) + "\n"


def sample_lane_note() -> str:
    return "# sample\n\n" + "\n".join(EXPECTED_LANE_LINES) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, sample_helper())
    write_file(root, MANIFEST_REL, sample_manifest())
    write_file(root, STRING_REVIEW_CHECKER_REL, sample_checker())
    write_file(root, LANE_NOTE_REL, sample_lane_note())


def run_self_test() -> int:
    cases = [
        "missing_file:tools/lib/string.zig",
        "helper:test \"memcpyAndPad copies the requested prefix and pads the destination tail\":expected=1:actual=0",
        "checker:test \"strchrNul and strchrnul return the first match or terminator boundary\":expected=1:actual=0",
        "lane:- the same string-local packet also keeps helper:expected=1:actual=0",
        "manifest:counted_search_review_anchors:expected=",
        "manifest:next_safe_step_note:expected=",
        "manifest:strnchr_review_summary:expected=",
        "manifest:strchrnul_review_anchor:expected=",
    ]

    with tempfile.TemporaryDirectory(prefix="phase1_string_direct_owner_alignment_") as tmp_dir:
        tmp_root = Path(tmp_dir)

        if cases[0] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:missing_file")

        build_sample_repo(tmp_root)
        if collect_failures(tmp_root):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:baseline")

        helper_path = tmp_root / STRING_HELPER_REL
        checker_path = tmp_root / STRING_REVIEW_CHECKER_REL
        lane_path = tmp_root / LANE_NOTE_REL
        manifest_path = tmp_root / MANIFEST_REL

        helper_path.write_text(helper_path.read_text(encoding="utf-8").replace(EXPECTED_COPY_FILL_ANCHORS[0] + "\n", "", 1), encoding="utf-8")
        if cases[1] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:helper_anchor")

        build_sample_repo(tmp_root)
        checker_path.write_text(checker_path.read_text(encoding="utf-8").replace(EXPECTED_COUNTED_SEARCH_ANCHORS[-1] + "\n", "", 1), encoding="utf-8")
        if cases[2] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:checker_anchor")

        build_sampleRepo = build_sample_repo
        build_sampleRepo(tmp_root)
        lane_path.write_text(lane_path.read_text(encoding="utf-8").replace(EXPECTED_LANE_LINES[0] + "\n", "", 1), encoding="utf-8")
        if cases[3] not in collect_failures(tmp_root):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:lane_line")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["counted_search_review_anchors"] = EXPECTED_COUNTED_SEARCH_ANCHORS[:-1]
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        failures = collect_failures(tmp_root)
        if not any(item.startswith(cases[4]) for item in failures):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:counted_search_manifest")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["next_safe_step_note"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        failures = collect_failures(tmp_root)
        if not any(item.startswith(cases[5]) for item in failures):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:next_safe_step_manifest")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["strnchr_review_summary"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        failures = collect_failures(tmp_root)
        if not any(item.startswith(cases[6]) for item in failures):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:review_summary_manifest")

        build_sample_repo(tmp_root)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["review_anchors"]["tools/lib/string.zig"]["strchrnul_review_anchor"] = "drift"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        failures = collect_failures(tmp_root)
        if not any(item.startswith(cases[7]) for item in failures):
            raise SystemExit("phase1-string-direct-owner-alignment:self-test:strchrnul_manifest")

    print("PHASE1_STRING_DIRECT_OWNER_ALIGNMENT_SELF_TEST=pass")
    print(f"PHASE1_STRING_DIRECT_OWNER_ALIGNMENT_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run checker self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_STRING_DIRECT_OWNER_ALIGNMENT=fail")
        for item in failures:
            print(item)
        return 1

    print("PHASE1_STRING_DIRECT_OWNER_ALIGNMENT=pass")
    print(f"PHASE1_STRING_DIRECT_OWNER_ALIGNMENT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE1_STRING_DIRECT_OWNER_ALIGNMENT_REQUIRED_ANCHOR_COUNT="
        f"{len(EXPECTED_COPY_FILL_ANCHORS) + len(EXPECTED_MEMTOSTR_ANCHORS) + len(EXPECTED_COUNTED_SEARCH_ANCHORS)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

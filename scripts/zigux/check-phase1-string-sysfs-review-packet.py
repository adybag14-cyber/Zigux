#!/usr/bin/env python3
"""Guard the live Phase 1 string sysfs review packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[3] if len(HERE.parents) > 3 else HERE.parent

STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_REVIEW_CHECKER_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")

REQUIRED_FILES = (
    STRING_HELPER_REL,
    STRING_REVIEW_CHECKER_REL,
    MANIFEST_REL,
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
)

EXPECTED_HELPER_ANCHORS = [
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
]

EXPECTED_HELPER_SYMBOLS = [
    "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "pub fn __sysfs_match_string(haystack: []const []const u8, count: usize, needle: []const u8) ?usize {",
    "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
]

EXPECTED_SYSFS_REVIEW_SUMMARY = (
    "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the "
    "direct string tests because the shared Phase 1 replay still carries no dedicated sysfs "
    "fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string "
    "remain review-visible at the helper surface"
)

EXPECTED_LANE_NOTE_LINES = {
    "direct_owner": (
        "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, "
        "memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality "
        "and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and "
        "sysfs_match_string(), C-string list lookup through matchString() and match_string(), "
        "counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte "
        "memchrInv coverage helper-local while the committed shared replay owns embedded-NUL "
        "replaceChar parity bytes and the current string fixture keys`"
    ),
    "sysfs_followup": (
        "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only "
        "shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, "
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and "
        "`scripts/zigux/check-phase1-string-review-packet.py`; the restored "
        "`Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` "
        "companions are now live broader reminder evidence on current `master`, but string should "
        "stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift."
    ),
    "next_safe_step": (
        "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside "
        "strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix "
        "boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() "
        "C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte "
        "memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the "
        "helper-local sysfs review anchors aligned across the string review packet and this lane note "
        "unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator "
        "names by default`"
    ),
}

EXPECTED_CLOSURE_LINES = {
    "string_tie_breaker": (
        "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor "
        "route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local "
        "sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, "
        "`sysfsMatchString()`, and `sysfs_match_string()`, or unless dedicated shared sysfs fixture keys "
        "land; do not reopen missing closure-side validator names or widen back into the broader "
        "helper-local string anchor family by default. Current `master` still keeps those sysfs review "
        "anchors explicit in `tools/lib/string.zig`, the committed manifest, "
        "`scripts/zigux/check-phase1-string-review-packet.py`, and "
        "`Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless "
        "those direct sysfs review surfaces drift or dedicated shared sysfs fixture keys land."
    ),
    "sysfs_review_marker": (
        "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order "
        "anchors stay explicit through the direct string tests and the Phase 1 helper manifest because "
        "the shared Phase 1 replay still carries no dedicated sysfs fixture keys`"
    ),
}

EXPECTED_REVIEW_CHECKER_MARKERS = {
    "source_symbol_sysfs_streq": "pub fn sysfsStreq(lhs: []const u8, rhs: []const u8) bool {",
    "source_symbol_sysfs_alias": "pub fn sysfs_streq(lhs: []const u8, rhs: []const u8) bool {",
    "source_symbol_sysfs_match": "pub fn sysfsMatchString(haystack: []const []const u8, needle: []const u8) ?usize {",
    "source_symbol_sysfs_match_alias": "pub fn sysfs_match_string(haystack: []const []const u8, needle: []const u8) ?usize {",
    "sysfs_anchor_primary": 'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    "sysfs_anchor_alias": 'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    "sysfs_anchor_match": 'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    "sysfs_anchor_match_alias": 'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
    "sysfs_review_summary": EXPECTED_SYSFS_REVIEW_SUMMARY,
    "next_safe_step_note": (
        "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across "
        "the string review packet and this lane note unless dedicated shared sysfs fixture keys "
        "land; do not reopen missing closure-side validator names by default."
    ),
}

EXPECTED_MANIFEST_PACKET = {
    "sysfs_review_anchors": EXPECTED_HELPER_ANCHORS,
    "sysfs_review_summary": EXPECTED_SYSFS_REVIEW_SUMMARY,
}


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


def require_exact_line(text: str, label: str, marker: str) -> list[str]:
    count = sum(1 for line in text.splitlines() if line.strip() == marker.strip())
    return [] if count == 1 else [f"{label}:expected=1:actual={count}"]


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
    for relative_path in REQUIRED_FILES:
        if not (root / relative_path).exists():
            failures.append(f"missing_file:{relative_path.as_posix()}")
    if failures:
        return failures

    helper_text = load_text(root, STRING_HELPER_REL)
    for symbol in EXPECTED_HELPER_SYMBOLS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_symbol:{symbol}", symbol))
    for anchor in EXPECTED_HELPER_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper_anchor:{anchor}", anchor))

    review_checker_text = load_text(root, STRING_REVIEW_CHECKER_REL)
    for key, marker in EXPECTED_REVIEW_CHECKER_MARKERS.items():
        failures.extend(require_exact_occurrence(review_checker_text, f"review_checker:{key}", marker))

    manifest = load_json(root, MANIFEST_REL)
    for key, expected in EXPECTED_MANIFEST_PACKET.items():
        failures.extend(
            require_exact_value(
                f"manifest:review_anchors.tools/lib/string.zig.{key}",
                nested_value(manifest, ("review_anchors", "tools/lib/string.zig", key)),
                expected,
            )
        )

    lane_note = load_text(root, LANE_NOTE_REL)
    for key, marker in EXPECTED_LANE_NOTE_LINES.items():
        failures.extend(require_exact_line(lane_note, f"lane_note:{key}", marker))

    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    for key, marker in EXPECTED_CLOSURE_LINES.items():
        failures.extend(require_exact_occurrence(closure_text, f"closure:{key}", marker))

    return failures


def write_file(root: Path, relative_path: Path, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_sample_repo(root: Path) -> None:
    write_file(
        root,
        STRING_HELPER_REL,
        "\n".join(EXPECTED_HELPER_SYMBOLS + EXPECTED_HELPER_ANCHORS) + "\n",
    )
    write_file(
        root,
        STRING_REVIEW_CHECKER_REL,
        "\n".join(EXPECTED_REVIEW_CHECKER_MARKERS.values()) + "\n",
    )
    write_file(
        root,
        MANIFEST_REL,
        json.dumps(
            {
                "review_anchors": {
                    "tools/lib/string.zig": EXPECTED_MANIFEST_PACKET,
                }
            },
            indent=2,
        )
        + "\n",
    )
    write_file(root, LANE_NOTE_REL, "\n".join(EXPECTED_LANE_NOTE_LINES.values()) + "\n")
    write_file(root, PHASE1_CLOSURE_REL, "\n".join(EXPECTED_CLOSURE_LINES.values()) + "\n")


def remove_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker + "\n" in text:
        text = text.replace(marker + "\n", "", 1)
    else:
        text = text.replace(marker, "", 1)
    path.write_text(text, encoding="utf-8")


def duplicate_marker(path: Path, marker: str) -> None:
    text = path.read_text(encoding="utf-8")
    text = text.replace(marker, marker + "\n" + marker, 1)
    path.write_text(text, encoding="utf-8")


def mutate_manifest(root: Path, key: str) -> None:
    manifest_path = root / MANIFEST_REL
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    packet = manifest["review_anchors"]["tools/lib/string.zig"]
    value = packet[key]
    if isinstance(value, list):
        packet[key] = value[1:]
    else:
        packet[key] = f"{value} drift"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_self_test() -> int:
    cases: list[tuple[str, tuple[Path, str, str] | tuple[str, str] | None]] = [("success", None)]

    for marker in EXPECTED_HELPER_ANCHORS:
        cases.append(("remove_helper_anchor", (STRING_HELPER_REL, marker, "remove")))
        cases.append(("duplicate_helper_anchor", (STRING_HELPER_REL, marker, "duplicate")))

    for key, marker in EXPECTED_REVIEW_CHECKER_MARKERS.items():
        if key == "sysfs_review_summary" or key.startswith("sysfs_anchor"):
            cases.append(("remove_review_marker", (STRING_REVIEW_CHECKER_REL, marker, "remove")))
            cases.append(("duplicate_review_marker", (STRING_REVIEW_CHECKER_REL, marker, "duplicate")))

    for marker in EXPECTED_LANE_NOTE_LINES.values():
        cases.append(("remove_lane_line", (LANE_NOTE_REL, marker, "remove")))

    for marker in EXPECTED_CLOSURE_LINES.values():
        cases.append(("remove_closure_line", (PHASE1_CLOSURE_REL, marker, "remove")))

    for key in EXPECTED_MANIFEST_PACKET:
        cases.append(("manifest_drift", (key, "manifest")))

    cases.append(("missing_file", (MANIFEST_REL, "", "missing_file")))
    cases.append(("missing_file", (STRING_REVIEW_CHECKER_REL, "", "missing_file")))

    for name, mutation in cases:
        with tempfile.TemporaryDirectory(prefix="phase1-string-sysfs-review-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            if mutation is not None:
                if len(mutation) == 3:
                    relative_path, marker, action = mutation
                    target = root / relative_path
                    if action == "remove":
                        remove_marker(target, marker)
                    elif action == "duplicate":
                        duplicate_marker(target, marker)
                    elif action == "missing_file":
                        target.unlink()
                else:
                    key, action = mutation
                    if action == "manifest":
                        mutate_manifest(root, key)

            failures = collect_failures(root)
            if name == "success":
                if failures:
                    print("PHASE1_STRING_SYSFS_REVIEW_PACKET_SELF_TEST=fail")
                    for failure in failures:
                        print(failure)
                    return 1
            elif not failures:
                print(f"self-test:{name}:expected_failure")
                return 1

    print("PHASE1_STRING_SYSFS_REVIEW_PACKET_SELF_TEST=pass")
    print(f"PHASE1_STRING_SYSFS_REVIEW_PACKET_SELF_TEST_CASE_COUNT={len(cases)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        print("PHASE1_STRING_SYSFS_REVIEW_PACKET=fail")
        for failure in failures:
            print(failure)
        return 1

    print("PHASE1_STRING_SYSFS_REVIEW_PACKET=pass")
    print(f"PHASE1_STRING_SYSFS_REVIEW_PACKET_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(f"PHASE1_STRING_SYSFS_REVIEW_PACKET_HELPER_ANCHOR_COUNT={len(EXPECTED_HELPER_ANCHORS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

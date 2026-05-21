#!/usr/bin/env python3
"""Guard the Phase 1 string sysfs review-rule packet against drift."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve()
DEFAULT_ROOT = HERE.parents[2] if len(HERE.parents) > 2 else HERE.parent

STRING_HELPER_REL = Path("tools/lib/string.zig")
STRING_PACKET_REL = Path("scripts/zigux/check-phase1-string-review-packet.py")
LANE_NOTE_REL = Path("Documentation/zigux/phase1-host-helper-lane-sequencing.md")
PHASE1_CLOSURE_REL = Path("Documentation/zigux/phase1-closure.md")
MANIFEST_REL = Path("zigux/tests/fixtures/phase1_helper_manifest.json")

REQUIRED_FILES = (
    STRING_HELPER_REL,
    STRING_PACKET_REL,
    LANE_NOTE_REL,
    PHASE1_CLOSURE_REL,
    MANIFEST_REL,
)

HELPER_SYSFS_ANCHORS = [
    'test "sysfsStreq treats trailing newline and NUL as equivalent"',
    'test "sysfs_streq mirrors sysfsStreq newline and NUL equivalence"',
    'test "sysfsMatchString finds newline-aware matches and preserves first-match order"',
    'test "sysfs_match_string mirrors sysfsMatchString for empty and matched lists"',
]

REVIEW_PACKET_EXACT_LINES = [
    '"sysfs_review_anchors": [',
    '"sysfs_review_summary": (',
    '"helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests because the shared Phase 1 replay still carries no dedicated sysfs fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string remain review-visible at the helper surface"',
    '"next_safe_step_note": (',
    '"If this helper lane reopens, keep the helper-local sysfs review anchors aligned across "',
    '"the string review packet and this lane note unless dedicated shared sysfs fixture keys "',
    '"land; do not reopen missing closure-side validator names by default."',
]

LANE_NOTE_EXACT_LINES = [
    "- `tools/lib/string.zig` keeps `strscpy()` and `strscpyPad()` copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, C-string list lookup through `matchString()` and `match_string()`, counted-search `strnchr()`, embedded-NUL trim preservation, and moving-earliest-dirty-byte `memchrInv()` coverage helper-local, while the committed shared replay still owns embedded-NUL `replaceChar` parity bytes and the current string fixture keys. Current `master` still exact-checks the manifest's memparse, matched-prefix and suffix, sysfs, C-string lookup, counted-search anchor groups, string review-summary scalars, and helper-specific `next_safe_step_note` through the shipped string review packet, while the older closure-side validator names are not directly readable in this environment; leave string parked unless those direct anchors drift, the helper-local sysfs review-anchor alignment between the string review packet and this lane note drifts, or committed shared-field drift appears.",
    "- the still-open string sysfs follow-through, if it reopens, should stay on one string-only shared review-rule packet across `zigux/tests/fixtures/phase1_helper_manifest.json`, `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and `scripts/zigux/check-phase1-string-review-packet.py`; the restored `Documentation/zigux/phase1-closure.md` and `scripts/zigux/validate-phase1-closure.py` companions are now live broader reminder evidence on current `master`, but string should stay parked on the helper-local sysfs review anchors unless those direct string surfaces drift.",
    "- `PHASE1_STRING_DIRECT_OWNER=string keeps strscpy()/strscpyPad() copy-and-pad semantics, memparse safety, matched-prefix-length and suffix boundary, sysfs newline-aware equality and lookup order through sysfsStreq(), sysfs_streq(), sysfsMatchString(), and sysfs_match_string(), C-string list lookup through matchString() and match_string(), counted-search strnchr, embedded-NUL trim preservation, and moving-earliest-dirty-byte memchrInv coverage helper-local while the committed shared replay owns embedded-NUL replaceChar parity bytes and the current string fixture keys`",
    "- `PHASE1_STRING_NEXT_SAFE_STEP=string reopens only for direct-anchor drift inside strscpy()/strscpyPad() copy-and-pad semantics, memparse, matched-prefix-length or suffix boundary, sysfs newline-aware equality or lookup order, matchString()/match_string() C-string list lookup, counted-search strnchr, embedded-NUL trim, or moving-earliest-dirty-byte memchrInv coverage, or for committed replaceChar or current string fixture drift; keep the helper-local sysfs review anchors aligned across the string review packet and this lane note unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names by default`",
]

CLOSURE_NOTE_EXACT_LINES = [
    "A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, or unless dedicated shared sysfs fixture keys land; do not reopen missing closure-side validator names or widen back into the broader helper-local string anchor family by default. Current `master` still keeps those sysfs review anchors explicit in `tools/lib/string.zig`, the committed manifest, `scripts/zigux/check-phase1-string-review-packet.py`, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless those direct sysfs review surfaces drift or dedicated shared sysfs fixture keys land.",
    "- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`",
]

MANIFEST_SYSFS_ANCHORS = HELPER_SYSFS_ANCHORS
MANIFEST_SYSFS_REVIEW_SUMMARY = (
    "helper-local sysfs newline-aware equality and lookup-order anchors stay explicit through the "
    "direct string tests because the shared Phase 1 replay still carries no dedicated sysfs "
    "fixture keys, so sysfsStreq and sysfs_streq plus sysfsMatchString and sysfs_match_string "
    "remain review-visible at the helper surface"
)
MANIFEST_NEXT_SAFE_STEP_NOTE = (
    "If this helper lane reopens, keep the helper-local sysfs review anchors aligned across the "
    "string review packet and this lane note unless dedicated shared sysfs fixture keys land; do "
    "not reopen missing closure-side validator names by default."
)


def repo_root(root: str | None) -> Path:
    return Path(root).resolve() if root else DEFAULT_ROOT.resolve()


def load_text(root: Path, relative_path: Path) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def load_json(root: Path, relative_path: Path) -> object:
    return json.loads(load_text(root, relative_path))


def nested_value(data: object, path: tuple[str, ...]) -> object:
    current = data
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def require_exact_occurrence(text: str, label: str, marker: str) -> list[str]:
    count = text.count(marker)
    if count != 1:
        return [f"{label}:expected=1:actual={count}"]
    return []


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
    packet_text = load_text(root, STRING_PACKET_REL)
    lane_text = load_text(root, LANE_NOTE_REL)
    closure_text = load_text(root, PHASE1_CLOSURE_REL)
    manifest = load_json(root, MANIFEST_REL)

    if not isinstance(manifest, dict):
        return [f"{MANIFEST_REL.as_posix()}:expected=dict:actual={type(manifest).__name__}"]

    for anchor in HELPER_SYSFS_ANCHORS:
        failures.extend(require_exact_occurrence(helper_text, f"helper:{anchor}", anchor))
        failures.extend(require_exact_occurrence(packet_text, f"packet_anchor:{anchor}", anchor))

    for line in REVIEW_PACKET_EXACT_LINES:
        failures.extend(require_exact_occurrence(packet_text, f"packet_line:{line[:40]}", line))
    for line in LANE_NOTE_EXACT_LINES:
        failures.extend(require_exact_occurrence(lane_text, f"lane_line:{line[:40]}", line))
    for line in CLOSURE_NOTE_EXACT_LINES:
        failures.extend(require_exact_occurrence(closure_text, f"closure_line:{line[:40]}", line))

    failures.extend(
        require_exact_value(
            "manifest:review_anchors.tools/lib/string.zig.sysfs_review_anchors",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "sysfs_review_anchors")),
            MANIFEST_SYSFS_ANCHORS,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:review_anchors.tools/lib/string.zig.sysfs_review_summary",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "sysfs_review_summary")),
            MANIFEST_SYSFS_REVIEW_SUMMARY,
        )
    )
    failures.extend(
        require_exact_value(
            "manifest:review_anchors.tools/lib/string.zig.next_safe_step_note",
            nested_value(manifest, ("review_anchors", "tools/lib/string.zig", "next_safe_step_note")),
            MANIFEST_NEXT_SAFE_STEP_NOTE,
        )
    )

    return failures


def write_file(root: Path, relative_path: Path, text: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sample_manifest() -> str:
    data = {
        "review_anchors": {
            "tools/lib/string.zig": {
                "sysfs_review_anchors": MANIFEST_SYSFS_ANCHORS,
                "sysfs_review_summary": MANIFEST_SYSFS_REVIEW_SUMMARY,
                "next_safe_step_note": MANIFEST_NEXT_SAFE_STEP_NOTE,
            }
        }
    }
    return json.dumps(data, indent=2) + "\n"


def build_sample_repo(root: Path) -> None:
    write_file(root, STRING_HELPER_REL, "\n".join(HELPER_SYSFS_ANCHORS) + "\n")
    write_file(
        root,
        STRING_PACKET_REL,
        "\n".join(HELPER_SYSFS_ANCHORS + REVIEW_PACKET_EXACT_LINES) + "\n",
    )
    write_file(root, LANE_NOTE_REL, "\n".join(LANE_NOTE_EXACT_LINES) + "\n")
    write_file(root, PHASE1_CLOSURE_REL, "\n".join(CLOSURE_NOTE_EXACT_LINES) + "\n")
    write_file(root, MANIFEST_REL, sample_manifest())


def run_self_test() -> int:
    case_count = 0

    with tempfile.TemporaryDirectory(prefix="phase1-string-sysfs-ok-") as tmpdir:
        root = Path(tmpdir)
        build_sample_repo(root)
        failures = collect_failures(root)
        if failures:
            print("self-test:success:unexpected_failures")
            for failure in failures:
                print(failure)
            return 1
        case_count += 1

    mutation_cases: list[tuple[str, Path, str]] = []
    mutation_cases.extend(("helper", STRING_HELPER_REL, anchor) for anchor in HELPER_SYSFS_ANCHORS)
    mutation_cases.extend(("packet_anchor", STRING_PACKET_REL, anchor) for anchor in HELPER_SYSFS_ANCHORS)
    mutation_cases.extend(("packet_line", STRING_PACKET_REL, line) for line in REVIEW_PACKET_EXACT_LINES)
    mutation_cases.extend(("lane_line", LANE_NOTE_REL, line) for line in LANE_NOTE_EXACT_LINES)
    mutation_cases.extend(("closure_line", PHASE1_CLOSURE_REL, line) for line in CLOSURE_NOTE_EXACT_LINES)

    for label, relative_path, marker in mutation_cases:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-sysfs-{label}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            path = root / relative_path
            text = path.read_text(encoding="utf-8")
            path.write_text(text.replace(marker + "\n", "", 1), encoding="utf-8")
            failures = collect_failures(root)
            if not failures:
                print(f"self-test:{label}:expected_failure")
                return 1
            case_count += 1

    manifest_paths = [
        ("sysfs_review_anchors", ("review_anchors", "tools/lib/string.zig", "sysfs_review_anchors")),
        ("sysfs_review_summary", ("review_anchors", "tools/lib/string.zig", "sysfs_review_summary")),
        ("next_safe_step_note", ("review_anchors", "tools/lib/string.zig", "next_safe_step_note")),
    ]

    for label, path_parts in manifest_paths:
        with tempfile.TemporaryDirectory(prefix=f"phase1-string-sysfs-manifest-{label}-") as tmpdir:
            root = Path(tmpdir)
            build_sample_repo(root)
            manifest_path = root / MANIFEST_REL
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            current = manifest
            for key in path_parts[:-1]:
                current = current[key]
            final_key = path_parts[-1]
            value = current[final_key]
            if isinstance(value, list):
                current[final_key] = value[1:]
            else:
                current[final_key] = f"{value} drift"
            manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
            failures = collect_failures(root)
            if not failures:
                print(f"self-test:manifest_{label}:expected_failure")
                return 1
            case_count += 1

    print("PHASE1_STRING_SYSFS_REVIEW_RULE_SELF_TEST=pass")
    print(f"PHASE1_STRING_SYSFS_REVIEW_RULE_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="override repository root for validation")
    parser.add_argument("--self-test", action="store_true", help="run the built-in checker self-test")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = collect_failures(repo_root(args.root))
    if failures:
        for failure in failures:
            print(failure)
        return 1

    print("phase1-string-sysfs-review-rule:ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 bsearch corpus packet."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

HELPER_PATH = Path("lib/bsearch.zig")
TEST_PATH = Path("zigux/tests/phase6_bsearch.zig")
LOWER_UPPER_PATH = Path("zigux/tests/phase6_bsearch_lower_bound_c_abi.zig")
EQUALITY_PATH = Path("zigux/tests/phase6_bsearch_c_abi_budget.zig")
FIXTURE_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")

EXPECTED_HELPER_ROW = {
    "key": "bsearch",
    "roadmap_anchor": "lib/bsearch.c",
    "zig_helper": "lib/bsearch.zig",
    "focused_helper_replay": "zigux/tests/phase6_bsearch.zig",
    "focused_c_abi_replays": [
        "zigux/tests/phase6_bsearch_lower_bound_c_abi.zig",
        "zigux/tests/phase6_bsearch_c_abi_budget.zig",
    ],
    "fixture_surfaces": [
        "zigux/tests/fixtures/phase6_bsearch_vectors.zig",
    ],
    "checker_surfaces": [
        "scripts/zigux/check-phase6-bsearch-corpus-evidence.py",
    ],
    "slice_note": "Documentation/zigux/phase6-bsearch-slice.md",
    "current_review_posture": "direct-helper-readback-restored",
}

EXPECTED_GAP_REMOVAL = "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"

REQUIRED_SNIPPETS = {
    HELPER_PATH.as_posix(): [
        "pub const RawComparator =",
        "pub const CRawComparator =",
        "pub fn equalRange(",
        "pub fn equalRangeMutable(",
        "pub fn bsearchEqualRange(",
        "pub fn bsearchEqualRangeMutable(",
    ],
    TEST_PATH.as_posix(): [
        'const fixtures = @import("fixtures/phase6_bsearch_vectors.zig");',
        "const values = fixtures.representative_ascending_values;",
        "const values = fixtures.representative_descending_values;",
        "const duplicates = fixtures.representative_duplicate_values;",
        'test "phase 6 bsearch keeps representative lookup work inside a binary-search budget"',
        'test "phase 6 bsearch keeps descending lookup work inside a binary-search budget"',
        'test "phase 6 bsearch raw lookup keeps representative work inside a binary-search budget"',
        'test "phase 6 bsearch bounded typed and raw equality probes stay inside a binary-search budget"',
        'test "phase 6 bsearch direct equalRange wrappers keep duplicate-span and write-through coverage aligned"',
        'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers"',
        'test "phase 6 bsearch keeps packed-record fixtures searchable through raw wrappers"',
    ],
    LOWER_UPPER_PATH.as_posix(): [
        'test "phase 6 bsearch raw c abi bounds keep duplicate spans and insertion points aligned"',
        'test "phase 6 bsearch descending raw c abi bounds stay comparator-driven"',
    ],
    EQUALITY_PATH.as_posix(): [
        'test "phase 6 bsearch raw c abi budgets stay logarithmic for deterministic ascending and descending slices"',
        'test "phase 6 bsearch raw c abi equal-range budgets stay logarithmic for duplicate spans in both sort orders"',
        'test "phase 6 bsearch runtime-selected raw c abi comparator pointers keep the budget contract"',
    ],
    FIXTURE_PATH.as_posix(): [
        "pub const representative_ascending_values = [_]u32{ 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45 };",
        "pub const representative_descending_values = [_]u32{ 45, 42, 39, 36, 33, 30, 27, 24, 21, 18, 15, 12, 9, 6, 3 };",
        "pub const representative_duplicate_values = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };",
        'test "phase 6 bsearch vectors stay deterministic, sorted, and duplicate-aware"',
    ],
    CATALOG_PATH.as_posix(): [
        "- direct corpus evidence checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        "- current review posture: direct helper-local evidence is readable again through `lib/bsearch.zig`, `zigux/tests/phase6_bsearch.zig`, `zigux/tests/phase6_bsearch_lower_bound_c_abi.zig`, `zigux/tests/phase6_bsearch_c_abi_budget.zig`, `zigux/tests/fixtures/phase6_bsearch_vectors.zig`, `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `Documentation/zigux/phase6-bsearch-slice.md`, this shared catalog, the machine-readable manifest, the restored shared build foothold, and the directly readable scripts-root plus tests-root reminders",
    ],
}

EXACT_OCCURRENCES = {
    TEST_PATH.as_posix(): [
        ("try std.testing.expect(counted_compare_calls <= 4);", 10),
        ("try std.testing.expect(counted_raw_compare_calls <= 4);", 10),
    ],
}


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def require_snippets(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(
                    f"missing expected Phase 6 bsearch marker in {rel_path}: {snippet}"
                )


def require_exact_occurrences(repo_root: Path) -> None:
    for rel_path, entries in EXACT_OCCURRENCES.items():
        content = read_text(repo_root / rel_path)
        for needle, expected in entries:
            found = content.count(needle)
            if found != expected:
                raise ValidationError(
                    f"expected {expected} occurrences in {rel_path}, found {found}: {needle}"
                )


def validate_manifest(repo_root: Path) -> None:
    manifest = json.loads(read_text(repo_root / MANIFEST_PATH))
    helpers = manifest.get("helpers")
    if not isinstance(helpers, list):
        raise ValidationError("missing helpers list in phase6_helper_evidence_manifest.json")
    helper = next(
        (row for row in helpers if isinstance(row, dict) and row.get("key") == "bsearch"),
        None,
    )
    if helper != EXPECTED_HELPER_ROW:
        raise ValidationError("bsearch helper row drifted in phase6_helper_evidence_manifest.json")

    gaps = manifest.get("current_repo_reality_gaps")
    if not isinstance(gaps, list):
        raise ValidationError("missing current_repo_reality_gaps in phase6_helper_evidence_manifest.json")
    if EXPECTED_GAP_REMOVAL in gaps:
        raise ValidationError("bsearch corpus checker still listed as a repo-reality gap")


def validate_catalog_absence(repo_root: Path) -> None:
    content = read_text(repo_root / CATALOG_PATH)
    stale_line = (
        "- last-known companion packet members still needing fresh direct reads: "
        "`scripts/zigux/check-phase6-bsearch-corpus-evidence.py`"
    )
    if stale_line in content:
        raise ValidationError("stale bsearch checker warning still present in helper-evidence catalog")


def validate(repo_root: Path) -> None:
    validate_manifest(repo_root)
    validate_catalog_absence(repo_root)
    require_snippets(repo_root)
    require_exact_occurrences(repo_root)


def scaffold_repo(root: Path) -> None:
    manifest = {
        "helpers": [EXPECTED_HELPER_ROW],
        "current_repo_reality_gaps": [
            "Documentation/zigux/phase6-helper-parity-catalog.md",
            "Documentation/zigux/phase6-perf-gate-survey.md",
        ],
    }
    write_text(root / MANIFEST_PATH, json.dumps(manifest, indent=2) + "\n")

    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        lines = list(dict.fromkeys(snippets))
        for needle, expected in EXACT_OCCURRENCES.get(rel_path, []):
            lines.extend([needle] * expected)
        write_text(root / rel_path, "\n".join(lines) + "\n")


def assert_failure(root: Path, rel_path: str, old: str, new: str) -> None:
    path = root / rel_path
    original = read_text(path)
    if old not in original:
        raise AssertionError(f"self-test marker missing from {rel_path}: {old}")
    write_text(path, original.replace(old, new, 1))
    try:
        validate(root)
    except ValidationError:
        write_text(path, original)
        return
    write_text(path, original)
    raise AssertionError(f"expected validation failure for {rel_path}")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"checker_surfaces": [\n        "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"\n      ]',
            '"checker_surfaces": []',
        )
        assert_failure(
            root,
            MANIFEST_PATH.as_posix(),
            '"current_repo_reality_gaps": [\n    "Documentation/zigux/phase6-helper-parity-catalog.md",\n    "Documentation/zigux/phase6-perf-gate-survey.md"\n  ]',
            '"current_repo_reality_gaps": [\n    "Documentation/zigux/phase6-helper-parity-catalog.md",\n    "Documentation/zigux/phase6-perf-gate-survey.md",\n    "scripts/zigux/check-phase6-bsearch-corpus-evidence.py"\n  ]',
        )
        assert_failure(
            root,
            CATALOG_PATH.as_posix(),
            "- direct corpus evidence checker: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
            "- last-known companion packet members still needing fresh direct reads: `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`",
        )
        assert_failure(
            root,
            TEST_PATH.as_posix(),
            'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator pointers"',
            'test "phase 6 bsearch accepts runtime-selected descending raw c abi comparator drift"',
        )
        assert_failure(
            root,
            FIXTURE_PATH.as_posix(),
            "pub const representative_duplicate_values = [_]u32{ 3, 6, 9, 12, 21, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };",
            "pub const representative_duplicate_values = [_]u32{ 3, 6, 9, 12, 21, 21, 24, 27, 30, 33, 36, 39, 42, 45 };",
        )

    print("PHASE6_BSEARCH_CORPUS_EVIDENCE_SELF_TEST=pass")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except (ValidationError, json.JSONDecodeError) as exc:
        print(f"PHASE6_BSEARCH_CORPUS_EVIDENCE=fail: {exc}")
        return 1
    print("PHASE6_BSEARCH_CORPUS_EVIDENCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

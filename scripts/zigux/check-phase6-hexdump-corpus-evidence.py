#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 hexdump corpus-evidence packet."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 hexdump corpus marker is missing."""


SLICE_PATH = Path("Documentation/zigux/phase6-hexdump-slice.md")
CATALOG_PATH = Path("Documentation/zigux/phase6-helper-evidence-catalog.md")
PARITY_CATALOG_PATH = Path("Documentation/zigux/phase6-helper-parity-catalog.md")
HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
HELPER_PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")
HELPER_TEST_PATH = Path("zigux/tests/phase6_hexdump.zig")
PERF_TEST_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
PERF_MATRIX_PATH = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
FIXTURES_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")

EXPECTED_COUNTS = {
    "parity_cases": 10,
    "overflow_cases": 4,
    "length_cases": 11,
    "perf_cases": 4,
}

EXPECTED_PERF_LABELS = [
    "16B-plain-g1",
    "32B-ascii-g2",
    "16B-ascii-g4",
    "16B-ascii-g8",
]

EXPECTED_LENGTH_CASES = [
    "empty plain line reports zero length",
    "empty ascii line reports zero length",
    "plain rowsize-16 group-1 line length",
    "ascii rowsize-16 group-1 line length",
    "plain rowsize-16 group-4 line length",
    "ascii rowsize-16 group-4 line length",
    "ascii rowsize-32 group-1 line length",
    "plain rowsize-16 group-8 line length",
    "ascii rowsize-16 group-8 line length",
    "normalized rowsize and groupsize fallback line length",
    "uneven group fallback line length",
]

EXPECTED_OVERFLOW_CASES = [
    "zero-sized caller buffer reports required ascii length",
    "short ascii buffer truncates but stays NUL terminated",
    "grouped plain buffer truncates deterministically",
    "normalized ascii buffer truncates after fallback formatting",
]

EXPECTED_SLICE_SNIPPETS = [
    "- `scripts/zigux/check-phase6-hexdump-corpus-evidence.py`",
    "- exact fixture-owned corpus counts on current `master`: 10 parity cases, 4 overflow cases, 11 curated length cases, and 4 perf replay cases, all centralized in `zigux/tests/fixtures/phase6_hexdump_vectors.zig` and replayed by `zigux/tests/phase6_hexdump.zig`, `zigux/tests/phase6_hexdump_perf.zig`, or `zigux/tests/phase6_hexdump_perf_matrix.zig`",
    "- the same fixture packet keeps rowsize normalization, uneven-groupsize fallback, grouped-output text, overflow truncation, and the four-case perf matrix reviewable without widening into neighboring Phase 6 helpers",
]

EXPECTED_CATALOG_SNIPPETS = [
    "- dedicated corpus checker: `scripts/zigux/check-phase6-hexdump-corpus-evidence.py`",
    "- exact fixture-owned corpus counts: 10 parity cases, 4 overflow cases, 11 curated length cases, and 4 perf replay cases in `zigux/tests/fixtures/phase6_hexdump_vectors.zig`",
]

EXPECTED_PARITY_CATALOG_SNIPPETS = [
    "`scripts/zigux/check-phase6-hexdump-corpus-evidence.py`",
    "direct helper readback is restored across the helper, focused replay, perf replay, perf-matrix preflight, fixture surface, dedicated corpus checker, packet checker, route checker, slice note, and perf-refresh rationale note",
]

EXPECTED_HELPER_TEST_SNIPPETS = [
    'test "phase 6 hexdump helper packet replays the serialized parity matrix" {',
    'test "phase 6 hexdump helper packet preserves the overflow contract" {',
    'test "phase 6 hexdump helper packet preserves the curated length matrix" {',
    'test "phase 6 hexdump direct helper entrypoints stay aligned with the packet" {',
    'test "phase 6 hexdump direct pack helpers keep uppercase and lowercase nibble parity" {',
]

EXPECTED_PERF_TEST_SNIPPETS = [
    "fn validatePerfMatrix() !void {",
    "fixtures.perf_cases",
    "PHASE6_HEXDUMP_PERF_CASE_COUNT",
    "error.HexdumpPerfRegression",
]

EXPECTED_PERF_MATRIX_SNIPPETS = [
    'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {',
    '.label = "16B-plain-g1",',
    '.label = "32B-ascii-g2",',
    '.label = "16B-ascii-g4",',
    '.label = "16B-ascii-g8",',
]

SELF_TEST_CASES = 12


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippets(path: Path, snippets: list[str]) -> None:
    content = read_text(path)
    for snippet in snippets:
        if snippet not in content:
            raise ValidationError(
                f"missing expected Phase 6 hexdump corpus marker in {path.as_posix()}: {snippet}"
            )


def extract_array_body(content: str, name: str) -> str:
    marker = f"pub const {name} ="
    start = content.find(marker)
    if start == -1:
        raise ValidationError(
            f"missing expected Phase 6 hexdump corpus array in {FIXTURES_PATH.as_posix()}: {name}"
        )

    brace_start = content.find("{", start)
    if brace_start == -1:
        raise ValidationError(
            f"missing opening brace for Phase 6 hexdump corpus array in {FIXTURES_PATH.as_posix()}: {name}"
        )

    depth = 0
    for idx in range(brace_start, len(content)):
        char = content[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[brace_start + 1 : idx]

    raise ValidationError(
        f"unterminated Phase 6 hexdump corpus array in {FIXTURES_PATH.as_posix()}: {name}"
    )


def count_entries(body: str) -> int:
    return len(re.findall(r"\.\{", body))


def validate_fixture_counts(content: str) -> None:
    for name, expected in EXPECTED_COUNTS.items():
        body = extract_array_body(content, name)
        actual = count_entries(body)
        if actual != expected:
            raise ValidationError(
                f"{FIXTURES_PATH.as_posix()} {name} count drift: expected {expected}, found {actual}"
            )


def validate_named_cases(content: str, array_name: str, expected_names: list[str], field: str) -> None:
    body = extract_array_body(content, array_name)
    actual_names = re.findall(rf'\.{field} = "([^"]+)"', body)
    if actual_names != expected_names:
        raise ValidationError(
            f"{FIXTURES_PATH.as_posix()} {array_name} {field} order drift: expected {expected_names}, found {actual_names}"
        )


def validate_perf_thresholds(content: str) -> None:
    body = extract_array_body(content, "perf_cases")
    thresholds = re.findall(r"\.max_slowdown_pct = (\d+)", body)
    if thresholds != ["175", "550", "550", "600"]:
        raise ValidationError(
            f"{FIXTURES_PATH.as_posix()} hexdump slowdown threshold drift: expected ['175', '550', '550', '600'], found {thresholds}"
        )


def validate(repo_root: Path) -> None:
    require_snippets(repo_root / SLICE_PATH, EXPECTED_SLICE_SNIPPETS)
    require_snippets(repo_root / CATALOG_PATH, EXPECTED_CATALOG_SNIPPETS)
    require_snippets(repo_root / PARITY_CATALOG_PATH, EXPECTED_PARITY_CATALOG_SNIPPETS)
    require_snippets(repo_root / HELPER_TEST_PATH, EXPECTED_HELPER_TEST_SNIPPETS)
    require_snippets(repo_root / PERF_TEST_PATH, EXPECTED_PERF_TEST_SNIPPETS)
    require_snippets(repo_root / PERF_MATRIX_PATH, EXPECTED_PERF_MATRIX_SNIPPETS)
    require_snippets(repo_root / HELPER_EVIDENCE_MANIFEST_PATH, [
        '"scripts/zigux/check-phase6-hexdump-corpus-evidence.py"',
        '"hexdump"',
        '"label": "16B-plain-g1"',
        '"label": "16B-ascii-g8"',
    ])
    require_snippets(repo_root / HELPER_PARITY_MANIFEST_PATH, [
        '"scripts/zigux/check-phase6-hexdump-corpus-evidence.py"',
        '"hexdump"',
        '"label": "16B-plain-g1"',
        '"label": "16B-ascii-g8"',
    ])

    fixtures_content = read_text(repo_root / FIXTURES_PATH)
    validate_fixture_counts(fixtures_content)
    validate_named_cases(fixtures_content, "length_cases", EXPECTED_LENGTH_CASES, "name")
    validate_named_cases(fixtures_content, "overflow_cases", EXPECTED_OVERFLOW_CASES, "name")
    validate_named_cases(fixtures_content, "perf_cases", EXPECTED_PERF_LABELS, "label")
    validate_perf_thresholds(fixtures_content)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(root / SLICE_PATH, "\n".join(EXPECTED_SLICE_SNIPPETS) + "\n")
    write(root / CATALOG_PATH, "\n".join(EXPECTED_CATALOG_SNIPPETS) + "\n")
    write(root / PARITY_CATALOG_PATH, "\n".join(EXPECTED_PARITY_CATALOG_SNIPPETS) + "\n")
    write(root / HELPER_TEST_PATH, "\n".join(EXPECTED_HELPER_TEST_SNIPPETS) + "\n")
    write(root / PERF_TEST_PATH, "\n".join(EXPECTED_PERF_TEST_SNIPPETS) + "\n")
    write(root / PERF_MATRIX_PATH, "\n".join(EXPECTED_PERF_MATRIX_SNIPPETS) + "\n")
    write(root / HELPER_EVIDENCE_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-corpus-evidence.py"\n"hexdump"\n"label": "16B-plain-g1"\n"label": "16B-ascii-g8"\n')
    write(root / HELPER_PARITY_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-corpus-evidence.py"\n"hexdump"\n"label": "16B-plain-g1"\n"label": "16B-ascii-g8"\n')
    write(
        root / FIXTURES_PATH,
        """pub const parity_cases = [_]ParityCase{
    .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{}, .{},
};
pub const overflow_cases = [_]OverflowCase{
    .{ .name = "zero-sized caller buffer reports required ascii length" },
    .{ .name = "short ascii buffer truncates but stays NUL terminated" },
    .{ .name = "grouped plain buffer truncates deterministically" },
    .{ .name = "normalized ascii buffer truncates after fallback formatting" },
};
pub const length_cases = [_]LengthCase{
    .{ .name = "empty plain line reports zero length" },
    .{ .name = "empty ascii line reports zero length" },
    .{ .name = "plain rowsize-16 group-1 line length" },
    .{ .name = "ascii rowsize-16 group-1 line length" },
    .{ .name = "plain rowsize-16 group-4 line length" },
    .{ .name = "ascii rowsize-16 group-4 line length" },
    .{ .name = "ascii rowsize-32 group-1 line length" },
    .{ .name = "plain rowsize-16 group-8 line length" },
    .{ .name = "ascii rowsize-16 group-8 line length" },
    .{ .name = "normalized rowsize and groupsize fallback line length" },
    .{ .name = "uneven group fallback line length" },
};
pub const perf_cases = [_]PerfCase{
    .{ .label = "16B-plain-g1", .max_slowdown_pct = 175 },
    .{ .label = "32B-ascii-g2", .max_slowdown_pct = 550 },
    .{ .label = "16B-ascii-g4", .max_slowdown_pct = 550 },
    .{ .label = "16B-ascii-g8", .max_slowdown_pct = 600 },
};
""",
    )


def expect_failure(root: Path, rel_path: Path, old: str, new: str) -> None:
    path = root / rel_path
    original = read_text(path)
    if old not in original:
        raise AssertionError(f"self-test marker not found in {rel_path.as_posix()}: {old}")
    write(path, original.replace(old, new, 1))
    try:
        validate(root)
    except ValidationError as exc:
        if rel_path.as_posix() not in str(exc):
            raise AssertionError(
                f"expected failure mentioning {rel_path.as_posix()}, got {exc}"
            ) from exc
    else:
        raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
    finally:
        write(path, original)


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="zigux_phase6_hexdump_corpus_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        expect_failure(root, SLICE_PATH, EXPECTED_SLICE_SNIPPETS[0], "- `scripts/zigux/check-phase6-hexdump-corpus-proof.py`")
        expect_failure(root, CATALOG_PATH, EXPECTED_CATALOG_SNIPPETS[1], "- exact fixture-owned corpus counts: 8 parity cases only")
        expect_failure(root, PARITY_CATALOG_PATH, "`scripts/zigux/check-phase6-hexdump-corpus-evidence.py`", "`scripts/zigux/check-phase6-hexdump-proof.py`")
        expect_failure(root, HELPER_TEST_PATH, EXPECTED_HELPER_TEST_SNIPPETS[2], 'test "phase 6 hexdump helper packet preserves the length matrix" {')
        expect_failure(root, PERF_TEST_PATH, EXPECTED_PERF_TEST_SNIPPETS[2], "PHASE6_HEXDUMP_PERF_TOTAL")
        expect_failure(root, PERF_MATRIX_PATH, EXPECTED_PERF_MATRIX_SNIPPETS[4], '.label = "16B-ascii-g16",')
        expect_failure(root, FIXTURES_PATH, '.{ .name = "normalized rowsize and groupsize fallback line length" },', '.{ .name = "normalized rowsize fallback line length" },')
        expect_failure(root, FIXTURES_PATH, '.{ .name = "normalized ascii buffer truncates after fallback formatting" },', '.{ .name = "normalized buffer truncates after fallback formatting" },')
        expect_failure(root, FIXTURES_PATH, '.{ .label = "16B-ascii-g8", .max_slowdown_pct = 600 },', '.{ .label = "16B-ascii-g8", .max_slowdown_pct = 550 },')
        expect_failure(root, HELPER_EVIDENCE_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-corpus-evidence.py"', '"scripts/zigux/check-phase6-hexdump-proof.py"')
        expect_failure(root, HELPER_PARITY_MANIFEST_PATH, '"scripts/zigux/check-phase6-hexdump-corpus-evidence.py"', '"scripts/zigux/check-phase6-hexdump-proof.py"')
        expect_failure(root, FIXTURES_PATH, 'pub const parity_cases = [_]ParityCase{', 'pub const parity_rows = [_]ParityCase{')
    print("PHASE6_HEXDUMP_CORPUS_EVIDENCE_SELF_TEST=pass")
    print(f"PHASE6_HEXDUMP_CORPUS_EVIDENCE_SELF_TEST_CASE_COUNT={SELF_TEST_CASES}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run built-in self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    validate(args.repo_root)
    print("PHASE6_HEXDUMP_CORPUS_EVIDENCE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Fail-closed checks for the current Phase 6 direct perf-threshold packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 perf marker is missing."""


BASE64_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_base64_vectors.zig")
BASE64_PERF_PATH = Path("zigux/tests/phase6_base64_perf.zig")
BASE64_SLICE_PATH = Path("Documentation/zigux/phase6-base64-slice.md")
BSEARCH_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_bsearch_vectors.zig")
BSEARCH_PERF_PATH = Path("zigux/tests/phase6_bsearch_perf.zig")
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")
PHASE6_HELPER_EVIDENCE_MANIFEST_PATH = Path("zigux/tests/phase6_helper_evidence_manifest.json")
PHASE6_HELPER_PARITY_MANIFEST_PATH = Path("zigux/tests/phase6_helper_parity_manifest.json")

REQUIRED_SNIPPETS = {
    BASE64_VECTORS_PATH: [
        '.{ .label = "STD_PAD", .payload = perf_payload, .padding = true, .variant_name = "std", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "STD_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "std", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "URLSAFE_PAD", .payload = perf_payload, .padding = true, .variant_name = "urlsafe", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "URLSAFE_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "urlsafe", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_PAD", .payload = perf_payload, .padding = true, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        "try std.testing.expectEqual(expected.len, perf_cases.len);",
        "try std.testing.expect(saw_std_pad);",
        "try std.testing.expect(saw_std_no_pad);",
        "try std.testing.expect(saw_urlsafe_pad);",
        "try std.testing.expect(saw_urlsafe_no_pad);",
        "try std.testing.expect(saw_imap_pad);",
        "try std.testing.expect(saw_imap_no_pad);",
    ],
    BASE64_PERF_PATH: [
        "for (fixtures.perf_cases, 0..) |case, idx| {",
        "for (fixtures.perf_cases[idx + 1 ..]) |other| {",
        "if (encode_slowdown > case.max_encode_slowdown_pct) {",
        "if (decode_slowdown > case.max_decode_slowdown_pct) {",
    ],
    BASE64_SLICE_PATH: [
        "- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate",
    ],
    PHASE6_HELPER_EVIDENCE_MANIFEST_PATH: [
        '      "key": "base64",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_base64_perf.zig",',
        '        "scripts/zigux/check-phase6-base64-corpus-determinism.py"',
        '      "current_perf_evidence": {',
        '          "STD_PAD",',
        '          "STD_NO_PAD",',
        '          "URLSAFE_PAD",',
        '          "URLSAFE_NO_PAD",',
        '          "IMAP_PAD",',
        '          "IMAP_NO_PAD"',
        '        "iterations": 12000,',
        '        "max_encode_slowdown_pct": 150,',
        '        "max_decode_slowdown_pct": 325,',
        '          "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-base64-perf",',
    ],
    PHASE6_HELPER_PARITY_MANIFEST_PATH: [
        '      "key": "base64",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_base64_perf.zig",',
        '      "slice_note": "Documentation/zigux/phase6-base64-slice.md",',
        '      "current_perf_evidence": {',
        '          "STD_PAD",',
        '          "STD_NO_PAD",',
        '          "URLSAFE_PAD",',
        '          "URLSAFE_NO_PAD",',
        '          "IMAP_PAD",',
        '          "IMAP_NO_PAD"',
        '        "iterations": 12000,',
        '        "max_encode_slowdown_pct": 150,',
        '        "max_decode_slowdown_pct": 325,',
        '          "zig build phase6-base64-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-base64-perf",',
        '      "key": "bsearch",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_bsearch_perf.zig",',
        '        "budget_model": "comparison_budget",',
        '          "len15",',
        '          "len64",',
        '          "len1024"',
        '        "query_count": 16,',
        '        "bound_budget_formula": "std.math.log2_int_ceil(len) + 1",',
        '          "zig build phase6-bsearch-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-bsearch-perf",',
        '      "key": "checksum",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_checksum_perf.zig",',
        '            "label": "64B",',
        '            "iterations": 200000,',
        '            "max_slowdown_pct": 150',
        '            "label": "1501B",',
        '            "iterations": 12000,',
        '          "IPV4_20B",',
        '          "IPV4_24B",',
        '          "IPV4_60B"',
        '          "zig build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-checksum-perf-matrix-test",',
        '          "zig build phase6-checksum-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-checksum-perf",',
        '      "key": "hexdump",',
        '      "dedicated_slowdown_replay": "zigux/tests/phase6_hexdump_perf.zig",',
        '      "perf_matrix_preflight": "zigux/tests/phase6_hexdump_perf_matrix.zig",',
        '            "label": "16B-plain-g1",',
        '            "reps": 40000,',
        '            "max_slowdown_pct": 175',
        '            "label": "32B-ascii-g2",',
        '            "reps": 10000,',
        '            "label": "16B-ascii-g4",',
        '            "reps": 20000,',
        '            "label": "16B-ascii-g8",',
        '            "max_slowdown_pct": 600',
        '          "zig build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig",',
        '          "make -C zigux phase6-hexdump-perf",',
    ],
    BSEARCH_VECTORS_PATH: [
        '.{ .label = "len15", .len = representative_ascending_values.len, .reps = 4_000 },',
        '.{ .label = "len64", .len = 64, .reps = 2_000 },',
        '.{ .label = "len1024", .len = 1_024, .reps = 250 },',
        "pub const query_count: usize = 16;",
        'test "phase 6 bsearch perf seeds stay deterministic" {',
    ],
    BSEARCH_PERF_PATH: [
        "const max_compare_budget = std.math.log2_int_ceil(usize, case.len) + 1;",
        "var ascending_queries: [fixtures.query_count]u32 = undefined;",
        "fixtures.seedDeterministicQueries(case.len, ascending_values, &ascending_queries, &ascending_expected_hits);",
        "var descending_queries: [fixtures.query_count]u32 = undefined;",
        "fixtures.seedDeterministicQueries(case.len, descending_values, &descending_queries, &descending_expected_hits);",
        "const descending_witness = try runWitnessCases(",
        "try std.testing.expect(ascending_witness.max_compare_calls <= max_compare_budget);",
        "try std.testing.expect(descending_witness.max_compare_calls <= max_compare_budget);",
        "try std.testing.expect(avg_compare_calls <= @as(f64, @floatFromInt(max_compare_budget)));",
        "try std.testing.expect(perf_stats.max_compare_calls <= max_compare_budget);",
        "witness_max_compare_calls={} witness_case_count={}",
    ],
    CHECKSUM_VECTORS_PATH: [
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150, .fingerprint = 0xb498_d304_d0ee_aea5 },',
        '.{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150, .fingerprint = 0xc457_3e1a_cc20_3461 },',
        "try std.testing.expectEqual(expected.len, perf_cases.len);",
    ],
    CHECKSUM_PERF_PATH: [
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        "for (fixtures.perf_cases) |case| {",
        "const helper_expected = checksum.compute(case.bytes);",
        "const reference_expected = referenceInternetChecksum(case.bytes);",
        'std.debug.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
        "for (fixtures.fast_path_cases) |case| {",
        "const fast_path_expected = checksum.ipFastCsum(case.header);",
        "const compute_expected = checksum.compute(case.header);",
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        "if (slowdown_pct > case.max_slowdown_pct) {",
    ],
    HEXDUMP_VECTORS_PATH: [
        '.{ .label = "16B-plain-g1", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175 },',
        '.{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550 },',
        '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550 },',
        '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600 },',
        "try std.testing.expectEqual(@as(usize, 4), perf_cases.len);",
    ],
    HEXDUMP_PERF_PATH: [
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        "if (slowdown_pct > case.max_slowdown_pct) {",
        'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {',
    ],
    PHASE6_BUILD_PATH: [
        'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
        'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
    ],
}

REQUIRED_SNIPPET_COUNTS = {
    PHASE6_HELPER_PARITY_MANIFEST_PATH: {
        '          "make -C zigux phase6-perf"': 4,
    },
}

SELF_TEST_CASES = [
    (
        BASE64_VECTORS_PATH,
        '.{ .label = "IMAP_PAD", .payload = perf_payload, .padding = true, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_PAD", .payload = perf_payload, .padding = true, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 350 },',
    ),
    (
        BASE64_PERF_PATH,
        "for (fixtures.perf_cases[idx + 1 ..]) |other| {",
        "for (fixtures.perf_cases[0..0]) |other| {",
    ),
    (
        BASE64_SLICE_PATH,
        "- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 12000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate",
        "- exact helper-local perf replay packet: ordered labels `STD_PAD`, `STD_NO_PAD`, `URLSAFE_PAD`, `URLSAFE_NO_PAD`, `IMAP_PAD`, and `IMAP_NO_PAD`, each with `iterations = 16000`, `max_encode_slowdown_pct = 150`, and `max_decode_slowdown_pct = 325`, owned once in `zigux/tests/fixtures/phase6_base64_vectors.zig` and replayed by the helper-local perf gate",
    ),
    (
        PHASE6_HELPER_EVIDENCE_MANIFEST_PATH,
        '        "max_decode_slowdown_pct": 325,',
        '        "max_decode_slowdown_pct": 350,',
    ),
    (
        PHASE6_HELPER_EVIDENCE_MANIFEST_PATH,
        '          "IMAP_NO_PAD"',
        '          "IMAP_NO_PADDING"',
    ),
    (
        PHASE6_HELPER_EVIDENCE_MANIFEST_PATH,
        '          "make -C zigux phase6-base64-perf",',
        '          "make -C zigux phase6-base64-benchmark",',
    ),
    (
        PHASE6_HELPER_PARITY_MANIFEST_PATH,
        '        "max_decode_slowdown_pct": 325,',
        '        "max_decode_slowdown_pct": 350,',
    ),
    (
        PHASE6_HELPER_PARITY_MANIFEST_PATH,
        '        "bound_budget_formula": "std.math.log2_int_ceil(len) + 1",',
        '        "bound_budget_formula": "std.math.log2_int_floor(len) + 1",',
    ),
    (
        PHASE6_HELPER_PARITY_MANIFEST_PATH,
        '          "IPV4_60B"',
        '          "IPV4_64B"',
    ),
    (
        PHASE6_HELPER_PARITY_MANIFEST_PATH,
        '            "reps": 40000,',
        '            "reps": 45000,',
    ),
    (
        PHASE6_HELPER_PARITY_MANIFEST_PATH,
        '          "make -C zigux phase6-perf"',
        '          "make -C zigux phase6-perf-gate"',
    ),
    (
        BSEARCH_VECTORS_PATH,
        '.{ .label = "len1024", .len = 1_024, .reps = 250 },',
        '.{ .label = "len2048", .len = 2_048, .reps = 250 },',
    ),
    (
        BSEARCH_PERF_PATH,
        "var ascending_queries: [fixtures.query_count]u32 = undefined;",
        "var perf_queries: [fixtures.query_count]u32 = undefined;",
    ),
    (
        BSEARCH_PERF_PATH,
        "fixtures.seedDeterministicQueries(case.len, ascending_values, &ascending_queries, &ascending_expected_hits);",
        "fixtures.seedDeterministicQueries(case.len, values, &ascending_queries, &ascending_expected_hits);",
    ),
    (
        BSEARCH_PERF_PATH,
        "const descending_witness = try runWitnessCases(",
        "const alternate_witness = try runWitnessCases(",
    ),
    (
        BSEARCH_PERF_PATH,
        "try std.testing.expect(descending_witness.max_compare_calls <= max_compare_budget);",
        "try std.testing.expect(descending_witness.max_compare_calls < max_compare_budget);",
    ),
    (
        BSEARCH_PERF_PATH,
        "try std.testing.expect(perf_stats.max_compare_calls <= max_compare_budget);",
        "try std.testing.expect(worst_compare_calls <= max_compare_budget);",
    ),
    (
        CHECKSUM_VECTORS_PATH,
        '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150, .fingerprint = 0xb498_d304_d0ee_aea5 },',
        '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150, .fingerprint = 0xb498_d304_d0ee_aea6 },',
    ),
    (
        CHECKSUM_PERF_PATH,
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct + 1 });',
    ),
    (
        HEXDUMP_VECTORS_PATH,
        '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 550 },',
        '.{ .label = "16B-ascii-g4", .len = 16, .rowsize = 16, .groupsize = 4, .ascii = true, .reps = 20_000, .max_slowdown_pct = 575 },',
    ),
    (
        HEXDUMP_PERF_PATH,
        "if (slowdown_pct > case.max_slowdown_pct) {",
        "if (slowdown_pct > case.max_slowdown_pct + 1) {",
    ),
    (
        PHASE6_BUILD_PATH,
        'const bsearch_perf_step = b.step("phase6-bsearch-perf", "Run Phase 6 bsearch helper perf gate");',
        'const bsearch_perf_step = b.step("phase6-bsearch-profile", "Run Phase 6 bsearch helper perf gate");',
    ),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc



def validate_snippet_counts(path: Path, content: str) -> None:
    required_counts = REQUIRED_SNIPPET_COUNTS.get(path)
    if required_counts is None:
        return
    for snippet, expected_count in required_counts.items():
        actual_count = content.count(snippet)
        if actual_count != expected_count:
            raise ValidationError(
                f"unexpected Phase 6 perf marker count in {path.as_posix()}: "
                f"expected {expected_count} occurrences of {snippet!r}, found {actual_count}"
            )



def validate(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(
                    f"missing expected Phase 6 perf marker in {rel_path.as_posix()}: {snippet}"
                )
        validate_snippet_counts(rel_path, content)



def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def scaffold_repo(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content_lines = list(snippets)
        required_counts = REQUIRED_SNIPPET_COUNTS.get(rel_path, {})
        for snippet, expected_count in required_counts.items():
            existing_count = content_lines.count(snippet)
            if existing_count < expected_count:
                content_lines.extend([snippet] * (expected_count - existing_count))
        write(root / rel_path, "\n".join(content_lines) + "\n")



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
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        for rel_path, old, new in SELF_TEST_CASES:
            expect_failure(root, rel_path, old, new)
    print("PHASE6_PERF_THRESHOLD_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_PERF_THRESHOLD_MARKERS_SELF_TEST_CASE_COUNT={len(SELF_TEST_CASES)}")



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root to validate (default: current directory)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run built-in self-test instead of validating a repository",
    )
    return parser.parse_args()



def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    validate(args.repo_root)
    print("PHASE6_PERF_THRESHOLD_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
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
CHECKSUM_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
HEXDUMP_VECTORS_PATH = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
HEXDUMP_PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")
PHASE6_BUILD_PATH = Path("zigux/tests/phase6_build.zig")

REQUIRED_SNIPPETS = {
    BASE64_VECTORS_PATH: [
        '.{ .label = "STD_PAD", .payload = perf_payload, .padding = true, .variant_name = "std", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "URLSAFE_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "urlsafe", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        "try std.testing.expectEqual(expected.len, perf_cases.len);",
    ],
    BASE64_PERF_PATH: [
        "for (fixtures.perf_cases, 0..) |case, idx| {",
        "for (fixtures.perf_cases[idx + 1 ..]) |other| {",
        "if (encode_slowdown > case.max_encode_slowdown_pct) {",
        "if (decode_slowdown > case.max_decode_slowdown_pct) {",
    ],
    CHECKSUM_VECTORS_PATH: [
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150, .fingerprint = 0xc457_3e1a_cc20_3461 },',
    ],
    CHECKSUM_PERF_PATH: [
        '.{ .label = "64B", .len = 64, .iterations = 200_000, .max_slowdown_pct = 150, .fingerprint = 0x3193_4305_ba03_9b45 },',
        '.{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150, .fingerprint = 0x457f_efb1_ea64_3164 },',
        'std.debug.print("PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        "if (slowdown_pct > case.max_slowdown_pct) {",
    ],
    HEXDUMP_VECTORS_PATH: [
        '.{ .label = "16B-plain-g1", .len = 16, .rowsize = 16, .groupsize = 1, .ascii = false, .reps = 40_000, .max_slowdown_pct = 175 },',
        '.{ .label = "32B-ascii-g2", .len = 32, .rowsize = 32, .groupsize = 2, .ascii = true, .reps = 10_000, .max_slowdown_pct = 550 },',
        '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600 },',
        'try std.testing.expectEqual(@as(usize, 4), perf_cases.len);',
    ],
    HEXDUMP_PERF_PATH: [
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, case.max_slowdown_pct });',
        "if (slowdown_pct > case.max_slowdown_pct) {",
        'test "phase 6 hexdump perf matrix preflight stays aligned with the documented packet" {',
    ],
    PHASE6_BUILD_PATH: [
        'const base64_perf_step = b.step("phase6-base64-perf", "Run Phase 6 base64 helper perf gate");',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
    ],
}

SELF_TEST_CASES = [
    (
        BASE64_VECTORS_PATH,
        '.{ .label = "IMAP_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 325 },',
        '.{ .label = "IMAP_NO_PAD", .payload = perf_payload, .padding = false, .variant_name = "imap", .iterations = 12000, .max_encode_slowdown_pct = 150, .max_decode_slowdown_pct = 350 },',
    ),
    (
        BASE64_PERF_PATH,
        "for (fixtures.perf_cases[idx + 1 ..]) |other| {",
        "for (fixtures.perf_cases[0..0]) |other| {",
    ),
    (
        CHECKSUM_VECTORS_PATH,
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 },',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 8_000, .max_slowdown_pct = 150 },',
    ),
    (
        CHECKSUM_PERF_PATH,
        '.{ .label = "1501B", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150, .fingerprint = 0x457f_efb1_ea64_3164 },',
        '.{ .label = "1501", .len = 1501, .iterations = 12_000, .max_slowdown_pct = 150, .fingerprint = 0x457f_efb1_ea64_3164 },',
    ),
    (
        HEXDUMP_VECTORS_PATH,
        '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 600 },',
        '.{ .label = "16B-ascii-g8", .len = 16, .rowsize = 16, .groupsize = 8, .ascii = true, .reps = 20_000, .max_slowdown_pct = 650 },',
    ),
    (
        HEXDUMP_PERF_PATH,
        "if (slowdown_pct > case.max_slowdown_pct) {",
        "if (slowdown_pct > case.max_slowdown_pct + 1) {",
    ),
    (
        PHASE6_BUILD_PATH,
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
        'const checksum_perf_step = b.step("phase6-checksum-perf-missing", "Run Phase 6 checksum helper perf gate");',
    ),
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc



def validate(repo_root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(repo_root / rel_path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(
                    f"missing expected Phase 6 perf marker in {rel_path.as_posix()}: {snippet}"
                )



def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")



def scaffold_repo(root: Path) -> None:
    for rel_path, snippets in REQUIRED_SNIPPETS.items():
        write(root / rel_path, "\n".join(snippets) + "\n")



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

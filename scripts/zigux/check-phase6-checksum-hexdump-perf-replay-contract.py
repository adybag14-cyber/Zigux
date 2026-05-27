#!/usr/bin/env python3
"""Fail closed on the current Phase 6 checksum/hexdump perf replay packet."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

CHECKSUM_PERF = Path("zigux/tests/phase6_checksum_perf.zig")
CHECKSUM_FIXTURES = Path("zigux/tests/fixtures/phase6_checksum_vectors.zig")
HEXDUMP_PERF = Path("zigux/tests/phase6_hexdump_perf.zig")
HEXDUMP_MATRIX = Path("zigux/tests/phase6_hexdump_perf_matrix.zig")
HEXDUMP_FIXTURES = Path("zigux/tests/fixtures/phase6_hexdump_vectors.zig")
PHASE6_BUILD = Path("zigux/tests/phase6_build.zig")
MAKEFILE = Path("zigux/Makefile")

REQUIRED_FILES = [
    CHECKSUM_PERF,
    CHECKSUM_FIXTURES,
    HEXDUMP_PERF,
    HEXDUMP_MATRIX,
    HEXDUMP_FIXTURES,
    PHASE6_BUILD,
    MAKEFILE,
]

REQUIRED_SNIPPETS = {
    CHECKSUM_PERF: [
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n"',
        'std.debug.print("PHASE6_CHECKSUM_PERF_64B=pass\\n"',
        'std.debug.print("PHASE6_CHECKSUM_PERF_1501B=pass\\n"',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n"',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_20B=pass\\n"',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_20B_UPDATED=pass\\n"',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_24B=pass\\n"',
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_60B=pass\\n"',
        'std.debug.print("PHASE6_CHECKSUM_PERF={s}\\n"',
    ],
    CHECKSUM_FIXTURES: [
        '.{ .label = "64B", .bytes = &perf_payload_64b, .iterations = 200_000, .max_slowdown_pct = 150 }',
        '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 }',
        '.{ .label = "IPV4_20B", .header = &ip_fast_csum_ipv4_20b, .iterations = 600_000, .max_slowdown_pct = 100 }',
        '.{ .label = "IPV4_20B_UPDATED", .header = &ip_fast_csum_ipv4_20b_updated, .iterations = 600_000, .max_slowdown_pct = 100 }',
        '.{ .label = "IPV4_24B", .header = &ip_fast_csum_ipv4_24b, .iterations = 500_000, .max_slowdown_pct = 100 }',
        '.{ .label = "IPV4_60B", .header = &ip_fast_csum_ipv4_60b, .iterations = 250_000, .max_slowdown_pct = 100 }',
    ],
    HEXDUMP_PERF: [
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n"',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_16B-plain-g1=pass\\n"',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_32B-ascii-g2=pass\\n"',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_16B-ascii-g4=pass\\n"',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_16B-ascii-g8=pass\\n"',
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF={s}\\n"',
    ],
    HEXDUMP_MATRIX: [
        '.label = "16B-plain-g1"',
        '.label = "32B-ascii-g2"',
        '.label = "16B-ascii-g4"',
        '.label = "16B-ascii-g8"',
        'var exact: [114]u8 = undefined;',
        'var truncated: [113]u8 = [_]u8{fixtures.fill_char} ** 113;',
    ],
    HEXDUMP_FIXTURES: [
        '.label = "16B-plain-g1"',
        '.label = "32B-ascii-g2"',
        '.label = "16B-ascii-g4"',
        '.label = "16B-ascii-g8"',
        '.max_slowdown_pct = 175',
        '.max_slowdown_pct = 550',
        '.max_slowdown_pct = 600',
        'pub const test_hexdump_buf_size = 32 * 3 + 2 + 32 + 1;',
    ],
    PHASE6_BUILD: [
        'const checksum_perf_matrix_test_step = b.step(',
        '"phase6-checksum-perf-matrix-test"',
        'const checksum_perf_step = b.step("phase6-checksum-perf", "Run Phase 6 checksum helper perf gate");',
        'const hexdump_review_step = b.step("phase6-hexdump-review", "Run Phase 6 hexdump perf-matrix review preflight");',
        '"phase6-hexdump-perf-matrix-test"',
        'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
    ],
    MAKEFILE: [
        "phase6-checksum-perf-matrix-test:",
        "$(ZIG) build phase6-checksum-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-checksum-perf:",
        "phase6-hexdump-review:",
        "$(ZIG) build phase6-hexdump-review --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-hexdump-perf-matrix-test:",
        "$(ZIG) build phase6-hexdump-perf-matrix-test --build-file zigux/tests/phase6_build.zig --summary all",
        "phase6-hexdump-perf:",
        "$(ZIG) build phase6-hexdump-perf --build-file zigux/tests/phase6_build.zig -Doptimize=ReleaseSafe --summary all",
    ],
}

SELF_TEST_CASE_COUNT = 7


class ValidationError(RuntimeError):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def validate(root: Path) -> None:
    missing = [path.as_posix() for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        raise ValidationError("missing required files: " + ", ".join(missing))

    for path, snippets in REQUIRED_SNIPPETS.items():
        content = read_text(root / path)
        for snippet in snippets:
            if snippet not in content:
                raise ValidationError(f"{path.as_posix()} drifted: {snippet}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    for path, snippets in REQUIRED_SNIPPETS.items():
        write(root / path, "\n".join(snippets) + "\n")


def expect_failure(fn) -> None:
    try:
        fn()
    except ValidationError:
        return
    raise AssertionError("expected validation failure")


def run_self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="phase6_perf_replay_contract_") as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)

        cases_run = 0

        def reset() -> None:
            scaffold_repo(root)

        def expect_mutation(mutator) -> None:
            nonlocal cases_run
            reset()
            mutator()
            expect_failure(lambda: validate(root))
            cases_run += 1

        expect_mutation(
            lambda: write(
                root / CHECKSUM_PERF,
                read_text(root / CHECKSUM_PERF).replace(
                    'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_IPV4_60B=pass\\n"', "", 1
                ),
            )
        )
        expect_mutation(
            lambda: write(
                root / CHECKSUM_FIXTURES,
                read_text(root / CHECKSUM_FIXTURES).replace(
                    '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 150 }',
                    '.{ .label = "1501B", .bytes = &perf_payload_1501b, .iterations = 12_000, .max_slowdown_pct = 180 }',
                    1,
                ),
            )
        )
        expect_mutation(
            lambda: write(
                root / HEXDUMP_PERF,
                read_text(root / HEXDUMP_PERF).replace(
                    'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_16B-ascii-g8=pass\\n"', "", 1
                ),
            )
        )
        expect_mutation(
            lambda: write(
                root / HEXDUMP_MATRIX,
                read_text(root / HEXDUMP_MATRIX).replace('var exact: [114]u8 = undefined;', "", 1),
            )
        )
        expect_mutation(
            lambda: write(
                root / HEXDUMP_FIXTURES,
                read_text(root / HEXDUMP_FIXTURES).replace('.max_slowdown_pct = 600', '.max_slowdown_pct = 650', 1),
            )
        )
        expect_mutation(
            lambda: write(
                root / PHASE6_BUILD,
                read_text(root / PHASE6_BUILD).replace(
                    'const hexdump_perf_step = b.step("phase6-hexdump-perf", "Run Phase 6 hexdump helper perf gate");',
                    "",
                    1,
                ),
            )
        )
        expect_mutation(lambda: (root / MAKEFILE).unlink())

        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_SELF_TEST=pass")
    print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0

    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT=fail: {exc}")
        return 1

    print("PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT=pass")
    print(f"PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_REQUIRED_FILE_COUNT={len(REQUIRED_FILES)}")
    print(
        "PHASE6_CHECKSUM_HEXDUMP_PERF_REPLAY_CONTRACT_REQUIRED_MARKER_COUNT="
        f"{sum(len(snippets) for snippets in REQUIRED_SNIPPETS.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

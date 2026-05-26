#!/usr/bin/env python3
"""Fail-closed checks for the Phase 6 checksum/hexdump runtime perf markers."""

from __future__ import annotations

import argparse
import re
import tempfile
from pathlib import Path

CHECKSUM_PERF_PATH = Path("zigux/tests/phase6_checksum_perf.zig")
HEXDUMP_PERF_PATH = Path("zigux/tests/phase6_hexdump_perf.zig")

EXPECTED_CHECKSUM_PAYLOAD_LABELS = ["64B", "1501B"]
EXPECTED_CHECKSUM_FAST_PATH_LABELS = [
    "IPV4_20B",
    "IPV4_20B_UPDATED",
    "IPV4_24B",
    "IPV4_60B",
]
EXPECTED_HEXDUMP_LABELS = [
    "16B-plain-g1",
    "32B-ascii-g2",
    "16B-ascii-g4",
    "16B-ascii-g8",
]

CHECKSUM_PAYLOAD_FIELDS = [
    "ITERATIONS",
    "HELPER_NS",
    "REFERENCE_NS",
    "SLOWDOWN_PCT",
    "THRESHOLD_PCT",
    "CHECKSUM",
]
CHECKSUM_FAST_PATH_FIELDS = [
    "ITERATIONS",
    "HELPER_NS",
    "COMPUTE_NS",
    "SLOWDOWN_PCT",
    "THRESHOLD_PCT",
    "CHECKSUM",
]
HEXDUMP_FIELDS = [
    "ITERATIONS",
    "HELPER_NS",
    "REFERENCE_NS",
    "SLOWDOWN_PCT",
    "THRESHOLD_PCT",
    "ACCUMULATOR",
]

SELF_TEST_CASE_COUNT = 19


class ValidationError(RuntimeError):
    """Raised when an expected Phase 6 runtime marker is missing or drifted."""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ValidationError(f"missing required file: {path.as_posix()}") from exc


def require_snippet(content: str, snippet: str, label: str) -> None:
    if snippet not in content:
        raise ValidationError(f"missing {label}: {snippet}")


def validate_checksum_runtime_markers(content: str) -> None:
    require_snippet(
        content,
        'std.debug.print("PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        "checksum case-count marker",
    )
    require_snippet(
        content,
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n", .{fixtures.fast_path_cases.len});',
        "checksum fast-path case-count marker",
    )
    require_snippet(
        content,
        'PHASE6_CHECKSUM_PERF={s}\\n',
        "checksum overall status marker",
    )

    for field in CHECKSUM_PAYLOAD_FIELDS:
        require_snippet(
            content,
            f'PHASE6_CHECKSUM_PERF_{{s}}_{field}={{d}}\\n',
            f"checksum payload {field} marker",
        )
    for field in CHECKSUM_FAST_PATH_FIELDS:
        require_snippet(
            content,
            f'PHASE6_CHECKSUM_IP_FAST_CSUM_{{s}}_{field}={{d}}\\n',
            f"checksum fast-path {field} marker",
        )

    require_snippet(
        content,
        'std.debug.print("PHASE6_CHECKSUM_PERF_{s}=fail\\n", .{case.label});',
        "checksum payload fail marker",
    )
    require_snippet(
        content,
        'std.debug.print("PHASE6_CHECKSUM_PERF_{s}=pass\\n", .{case.label});',
        "checksum payload pass marker",
    )
    require_snippet(
        content,
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}=fail\\n", .{case.label});',
        "checksum fast-path fail marker",
    )
    require_snippet(
        content,
        'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}=pass\\n", .{case.label});',
        "checksum fast-path pass marker",
    )


def extract_declared_labels(content: str) -> list[str]:
    return re.findall(r'\.label = "([^"]+)"', content)


def validate_checksum_markers_by_label(content: str) -> None:
    declared_labels = extract_declared_labels(content)
    payload_labels = declared_labels[: len(EXPECTED_CHECKSUM_PAYLOAD_LABELS)]
    fast_path_labels = declared_labels[
        len(EXPECTED_CHECKSUM_PAYLOAD_LABELS) : len(EXPECTED_CHECKSUM_PAYLOAD_LABELS) + len(EXPECTED_CHECKSUM_FAST_PATH_LABELS)
    ]
    if payload_labels != EXPECTED_CHECKSUM_PAYLOAD_LABELS:
        raise ValidationError(f"checksum payload marker family labels drifted: {payload_labels}")
    if fast_path_labels != EXPECTED_CHECKSUM_FAST_PATH_LABELS:
        raise ValidationError(f"checksum fast-path marker family labels drifted: {fast_path_labels}")

    for field in CHECKSUM_PAYLOAD_FIELDS:
        require_snippet(
            content,
            f'PHASE6_CHECKSUM_PERF_{{s}}_{field}={{d}}\\n',
            f"checksum payload {field} marker",
        )
    if 'PHASE6_CHECKSUM_PERF_{s}=fail\\n' not in content or 'PHASE6_CHECKSUM_PERF_{s}=pass\\n' not in content:
        raise ValidationError("checksum payload status markers drifted")

    for field in CHECKSUM_FAST_PATH_FIELDS:
        require_snippet(
            content,
            f'PHASE6_CHECKSUM_IP_FAST_CSUM_{{s}}_{field}={{d}}\\n',
            f"checksum fast-path {field} marker",
        )
    if (
        'PHASE6_CHECKSUM_IP_FAST_CSUM_{s}=fail\\n' not in content
        or 'PHASE6_CHECKSUM_IP_FAST_CSUM_{s}=pass\\n' not in content
    ):
        raise ValidationError("checksum fast-path status markers drifted")


def validate_hexdump_runtime_markers(content: str) -> None:
    declared_labels = extract_declared_labels(content)
    hexdump_labels = declared_labels[: len(EXPECTED_HEXDUMP_LABELS)]
    if hexdump_labels != EXPECTED_HEXDUMP_LABELS:
        raise ValidationError(f"hexdump labels drifted: {hexdump_labels}")

    require_snippet(
        content,
        'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n", .{fixtures.perf_cases.len});',
        "hexdump case-count marker",
    )
    require_snippet(
        content,
        'PHASE6_HEXDUMP_PERF={s}\\n',
        "hexdump overall status marker",
    )
    require_snippet(
        content,
        "try stdout_writer.interface.flush();",
        "hexdump flush",
    )

    for field in HEXDUMP_FIELDS:
        require_snippet(
            content,
            f'PHASE6_HEXDUMP_PERF_{{s}}_{field}={{d}}\\n',
            f"hexdump {field} marker",
        )
    if 'PHASE6_HEXDUMP_PERF_{s}=fail\\n' not in content or 'PHASE6_HEXDUMP_PERF_{s}=pass\\n' not in content:
        raise ValidationError("hexdump status markers drifted")


def validate(repo_root: Path) -> None:
    checksum_content = read_text(repo_root / CHECKSUM_PERF_PATH)
    hexdump_content = read_text(repo_root / HEXDUMP_PERF_PATH)

    validate_checksum_runtime_markers(checksum_content)
    validate_checksum_markers_by_label(checksum_content)
    validate_hexdump_runtime_markers(hexdump_content)


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def scaffold_repo(root: Path) -> None:
    write(
        root / CHECKSUM_PERF_PATH,
        """const fixtures = struct {
    const perf_cases = [_]struct { label: []const u8 }{
        .{ .label = \"64B\" },
        .{ .label = \"1501B\" },
    };
    const fast_path_cases = [_]struct { label: []const u8 }{
        .{ .label = \"IPV4_20B\" },
        .{ .label = \"IPV4_20B_UPDATED\" },
        .{ .label = \"IPV4_24B\" },
        .{ .label = \"IPV4_60B\" },
    };
};
pub fn main() void {
    std.debug.print(\"PHASE6_CHECKSUM_PERF_CASE_COUNT={d}\\n\", .{fixtures.perf_cases.len});
    for (fixtures.perf_cases) |case| {
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}_ITERATIONS={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}_HELPER_NS={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}_REFERENCE_NS={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}_SLOWDOWN_PCT={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}_THRESHOLD_PCT={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}_CHECKSUM={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}=fail\\n\", .{case.label});
        std.debug.print(\"PHASE6_CHECKSUM_PERF_{s}=pass\\n\", .{case.label});
    }
    std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT={d}\\n\", .{fixtures.fast_path_cases.len});
    for (fixtures.fast_path_cases) |case| {
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_ITERATIONS={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_HELPER_NS={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_COMPUTE_NS={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_SLOWDOWN_PCT={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_THRESHOLD_PCT={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_CHECKSUM={d}\\n\", .{ case.label, 1 });
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}=fail\\n\", .{case.label});
        std.debug.print(\"PHASE6_CHECKSUM_IP_FAST_CSUM_{s}=pass\\n\", .{case.label});
    }
    std.debug.print(\"PHASE6_CHECKSUM_PERF={s}\\n\", .{if (false) \"fail\" else \"pass\"});
}
""",
    )
    write(
        root / HEXDUMP_PERF_PATH,
        """const fixtures = struct {
    const perf_cases = [_]struct { label: []const u8 }{
        .{ .label = \"16B-plain-g1\" },
        .{ .label = \"32B-ascii-g2\" },
        .{ .label = \"16B-ascii-g4\" },
        .{ .label = \"16B-ascii-g8\" },
    };
};
pub fn main() !void {
    try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_CASE_COUNT={d}\\n\", .{fixtures.perf_cases.len});
    for (fixtures.perf_cases) |case| {
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}_ITERATIONS={d}\\n\", .{ case.label, 1 });
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}_HELPER_NS={d}\\n\", .{ case.label, 1 });
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}_REFERENCE_NS={d}\\n\", .{ case.label, 1 });
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}_SLOWDOWN_PCT={d}\\n\", .{ case.label, 1 });
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}_THRESHOLD_PCT={d}\\n\", .{ case.label, 1 });
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}_ACCUMULATOR={d}\\n\", .{ case.label, 1 });
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}=fail\\n\", .{case.label});
        try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF_{s}=pass\\n\", .{case.label});
    }
    try stdout_writer.interface.print(\"PHASE6_HEXDUMP_PERF={s}\\n\", .{if (false) \"fail\" else \"pass\"});
    try stdout_writer.interface.flush();
}
""",
    )


def mutate_text(path: Path, old: str, new: str) -> None:
    content = read_text(path)
    if old not in content:
        raise AssertionError(f"expected seed snippet not found in {path.as_posix()}: {old}")
    write(path, content.replace(old, new, 1))


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        scaffold_repo(root)
        validate(root)
        cases_run = 0
        cases = [
            (CHECKSUM_PERF_PATH, "PHASE6_CHECKSUM_PERF_CASE_COUNT", "PHASE6_CHECKSUM_PERF_TOTAL_COUNT", "checksum case-count marker"),
            (CHECKSUM_PERF_PATH, "PHASE6_CHECKSUM_IP_FAST_CSUM_CASE_COUNT", "PHASE6_CHECKSUM_FAST_PATH_CASE_COUNT", "checksum fast-path case-count marker"),
            (CHECKSUM_PERF_PATH, "PHASE6_CHECKSUM_PERF_{s}_REFERENCE_NS", "PHASE6_CHECKSUM_PERF_{s}_REFERENCE_TIME", "checksum payload REFERENCE_NS marker"),
            (CHECKSUM_PERF_PATH, "PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_COMPUTE_NS", "PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_COMPUTE_TIME", "checksum fast-path COMPUTE_NS marker"),
            (CHECKSUM_PERF_PATH, 'std.debug.print("PHASE6_CHECKSUM_PERF_{s}=pass\\n", .{case.label});', "", "checksum payload pass marker"),
            (CHECKSUM_PERF_PATH, 'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}=pass\\n", .{case.label});', "", "checksum fast-path pass marker"),
            (CHECKSUM_PERF_PATH, '.{ .label = "1501B" },', '.{ .label = "1500B" },', "checksum payload marker family labels drifted"),
            (CHECKSUM_PERF_PATH, '.{ .label = "IPV4_60B" },', '.{ .label = "IPV4_64B" },', "checksum fast-path marker family labels drifted"),
            (CHECKSUM_PERF_PATH, 'std.debug.print("PHASE6_CHECKSUM_PERF={s}\\n", .{if (false) "fail" else "pass"});', "", "checksum overall status marker"),
            (HEXDUMP_PERF_PATH, "PHASE6_HEXDUMP_PERF_CASE_COUNT", "PHASE6_HEXDUMP_PERF_TOTAL_COUNT", "hexdump case-count marker"),
            (HEXDUMP_PERF_PATH, "PHASE6_HEXDUMP_PERF_{s}_REFERENCE_NS", "PHASE6_HEXDUMP_PERF_{s}_REFERENCE_TIME", "hexdump REFERENCE_NS marker"),
            (HEXDUMP_PERF_PATH, "PHASE6_HEXDUMP_PERF_{s}_ACCUMULATOR", "PHASE6_HEXDUMP_PERF_{s}_CHECKSUM", "hexdump ACCUMULATOR marker"),
            (HEXDUMP_PERF_PATH, 'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF_{s}=pass\\n", .{case.label});', "", "hexdump status markers drifted"),
            (HEXDUMP_PERF_PATH, '.{ .label = "16B-ascii-g8" },', '.{ .label = "16B-ascii-g16" },', "hexdump labels drifted"),
            (HEXDUMP_PERF_PATH, "try stdout_writer.interface.flush();", "", "hexdump flush"),
            (HEXDUMP_PERF_PATH, 'try stdout_writer.interface.print("PHASE6_HEXDUMP_PERF={s}\\n", .{if (false) "fail" else "pass"});', "", "hexdump overall status marker"),
            (CHECKSUM_PERF_PATH, '.{ .label = "64B" },', '.{ .label = "1501B" },', "checksum payload marker family labels drifted"),
            (HEXDUMP_PERF_PATH, '.{ .label = "32B-ascii-g2" },', '.{ .label = "16B-plain-g1" },', "hexdump labels drifted"),
            (CHECKSUM_PERF_PATH, 'std.debug.print("PHASE6_CHECKSUM_IP_FAST_CSUM_{s}_THRESHOLD_PCT={d}\\n", .{ case.label, 1 });', "", "checksum fast-path THRESHOLD_PCT marker"),
        ]
        for rel_path, old, new, expected in cases:
            mutate_text(root / rel_path, old, new)
            try:
                validate(root)
            except ValidationError as exc:
                if expected not in str(exc):
                    raise AssertionError(f"expected {expected!r} in {str(exc)!r}") from exc
            else:
                raise AssertionError(f"expected validation failure for {rel_path.as_posix()}")
            finally:
                scaffold_repo(root)
            cases_run += 1
        if cases_run != SELF_TEST_CASE_COUNT:
            raise AssertionError(f"expected {SELF_TEST_CASE_COUNT} cases, ran {cases_run}")
    print("PHASE6_RUNTIME_OUTPUT_MARKERS_SELF_TEST=pass")
    print(f"PHASE6_RUNTIME_OUTPUT_MARKERS_SELF_TEST_CASE_COUNT={cases_run}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="repository root to validate")
    parser.add_argument("--self-test", action="store_true", help="run the built-in self-test")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        run_self_test()
        return 0
    try:
        validate(args.repo_root)
    except ValidationError as exc:
        print(f"PHASE6_RUNTIME_OUTPUT_MARKERS=fail: {exc}")
        return 1
    print("PHASE6_RUNTIME_OUTPUT_MARKERS=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

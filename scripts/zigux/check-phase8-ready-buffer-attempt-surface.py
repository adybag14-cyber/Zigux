#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

HELPER_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"

HELPER_MARKERS = [
    "pub const ReadyBufferAttemptLookupDisposition = enum {",
    "pub const ReadyBufferAttemptLookupSummary = struct {",
    "requested_attempt_index: usize,",
    "ready_index: ?usize,",
    "ready_count: usize,",
    "pub const ReadyBufferAttemptLookupError = error{",
    "pub fn resolveReadyBufferAttemptIndex(",
    "pub fn summarizeReadyBufferAttemptLookup(",
    "pub fn resolveReadyBufferAttemptLookup(",
    'test "phase8 perf-buffer poll resolves ready-buffer attempt ordinals back to slot indexes" {',
    'test "phase8 perf-buffer poll exposes typed ready-buffer attempt lookup summaries" {',
    "try std.testing.expectEqual(@as(?usize, 1), resolveReadyBufferAttemptIndex(&buffers, 0));",
    "try std.testing.expectEqual(@as(usize, 2), first.ready_count);",
    "try std.testing.expectError(error.MissingReadyBuffer, resolveReadyBufferAttemptLookup(missing));",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    if not (root / HELPER_PATH).exists():
        failures.append(f"missing_file:{HELPER_PATH}")
    if failures:
        return failures

    text = read_text(root, HELPER_PATH)
    for marker in HELPER_MARKERS:
        if marker not in text:
            failures.append(f"missing_marker:{HELPER_PATH}:{marker}")
    return failures


def build_fixture_root(root: Path) -> None:
    write_text(root, HELPER_PATH, "\n".join(HELPER_MARKERS) + "\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8-ready-buffer-attempt-surface-") as tmp:
        base = Path(tmp)
        build_fixture_root(base)

        baseline = validate(base)
        if baseline:
            raise SystemExit(f"fixture tree should pass but failed: {baseline!r}")

        baseline_text = "\n".join(HELPER_MARKERS) + "\n"
        for marker in HELPER_MARKERS:
            write_text(base, HELPER_PATH, baseline_text.replace(marker, "", 1))
            expect_failure(base, f"missing_marker:{HELPER_PATH}:{marker}")
            write_text(base, HELPER_PATH, baseline_text)

        path = base / HELPER_PATH
        original = path.read_text(encoding="utf-8")
        path.unlink()
        expect_failure(base, f"missing_file:{HELPER_PATH}")
        write_text(base, HELPER_PATH, original)

    print("PHASE8_READY_BUFFER_ATTEMPT_SURFACE_SELF_TEST=pass")
    print(f"PHASE8_READY_BUFFER_ATTEMPT_SURFACE_HELPER_MARKER_COUNT={len(HELPER_MARKERS)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the surviving Phase 8 perf-buffer poll packet keeps the "
            "ready-buffer-attempt helper surfaces explicit inside the helper file."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="repository root to inspect",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="run the built-in checker self-test and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.repo_root)
    if failures:
        for failure in failures:
            print(f"PHASE8_READY_BUFFER_ATTEMPT_SURFACE_ERROR={failure}")
        return 1

    print(f"PHASE8_READY_BUFFER_ATTEMPT_SURFACE_HELPER_MARKER_COUNT={len(HELPER_MARKERS)}")
    print("PHASE8_READY_BUFFER_ATTEMPT_SURFACE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

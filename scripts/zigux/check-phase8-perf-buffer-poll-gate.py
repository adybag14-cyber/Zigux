#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import tempfile


SELF_PATH = Path(__file__).resolve()


def infer_repo_root() -> Path:
    for candidate in [SELF_PATH.parent, *SELF_PATH.parents]:
        if (candidate / "zigux/tests/phase8_perf_buffer_poll.zig").exists():
            return candidate
    return SELF_PATH.parent


ROOT = infer_repo_root()
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
PERF_BUFFER_POLL_TEST_PATH = "zigux/tests/phase8_perf_buffer_poll.zig"

SCRIPTS_README_REQUIRED_MARKERS = [
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "Phase 8 flow",
    "userspace-adjacent tooling",
]

TESTS_README_REQUIRED_MARKERS = [
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
]

PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS = [
    'test "phase 8 perf-buffer poll docs keep the bounded wait-result helper explicit" {',
    'test "phase 8 perf-buffer poll bridge survey keeps the bounded helper packet explicit" {',
    'test "phase 8 perf-buffer poll helper keeps the final return-path bookkeeping below routing parity" {',
    'test "phase 8 perf-buffer poll helper rejects ready waits without processing attempts" {',
    'test "phase 8 perf-buffer poll helper keeps buffer-fd lookup returns compact and errno-shaped" {',
    'test "phase 8 perf-buffer poll helper keeps buffer-window lookup returns compact and mapped-size-shaped" {',
    'test "resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries" {',
    '"Documentation/zigux/phase8-perf-buffer-poll-slice.md"',
    '"Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"',
    '"python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py"',
    "summarizePollExecutionResultFromWaitResult",
    "summarizeBufferFdLookup",
    "summarizeBufferWindowLookup",
    "resolveBufferFdLookupReturn",
    "resolveBufferWindowLookupReturn",
    "PollReturnDisposition.ready_count",
    "PollReturnDisposition.processing_failed",
    "first_process_error_index",
    "PollError.InconsistentProcessingAccountingSummary",
    "BufferFdLookupDisposition.missing_fd",
    "BufferWindowLookupDisposition.missing_window",
    "PollError.WaitResultDisagreesWithExecutionOutcome",
    "PollError.WaitResultDisagreesWithReadyEventCount",
    "PollError.WaitResultDisagreesWithFailureCode",
    "_ = resolvePollExecutionResultFromWaitResult;",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path in (SCRIPTS_README_PATH, TESTS_README_PATH, PERF_BUFFER_POLL_TEST_PATH):
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    scripts_readme = read_text(root, SCRIPTS_README_PATH)
    for marker in SCRIPTS_README_REQUIRED_MARKERS:
        if marker not in scripts_readme:
            failures.append(f"missing_marker:{SCRIPTS_README_PATH}:{marker}")

    tests_readme = read_text(root, TESTS_README_PATH)
    for marker in TESTS_README_REQUIRED_MARKERS:
        if marker not in tests_readme:
            failures.append(f"missing_marker:{TESTS_README_PATH}:{marker}")

    perf_buffer_poll_test = read_text(root, PERF_BUFFER_POLL_TEST_PATH)
    for marker in PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS:
        if marker not in perf_buffer_poll_test:
            failures.append(f"missing_marker:{PERF_BUFFER_POLL_TEST_PATH}:{marker}")

    return failures


def build_scripts_readme_fixture() -> str:
    return """# scripts/zigux

## Phase 8

- Phase 8 flow - current userspace-adjacent tooling keeps the bounded perf-buffer poll packet explicit from the scripts root
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
"""


def build_tests_readme_fixture() -> str:
    return """# zigux/tests

Phase 8 review packet
  * `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
  * `zigux/tests/phase8_perf_buffer_poll.zig`
  * `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  * `make -C zigux phase8-perf-buffer-poll-test`
"""


def build_perf_buffer_poll_test_fixture() -> str:
    return """const std = @import("std");

test "phase 8 perf-buffer poll docs keep the bounded wait-result helper explicit" {
    _ = "Documentation/zigux/phase8-perf-buffer-poll-slice.md";
}

test "phase 8 perf-buffer poll bridge survey keeps the bounded helper packet explicit" {
    _ = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md";
    _ = "python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py";
}

test "phase 8 perf-buffer poll helper keeps the final return-path bookkeeping below routing parity" {
    _ = summarizePollExecutionResultFromWaitResult;
    _ = PollReturnDisposition.ready_count;
    _ = PollReturnDisposition.processing_failed;
    _ = first_process_error_index;
}

test "phase 8 perf-buffer poll helper rejects ready waits without processing attempts" {
    _ = PollError.InconsistentProcessingAccountingSummary;
}

test "phase 8 perf-buffer poll helper keeps buffer-fd lookup returns compact and errno-shaped" {
    _ = summarizeBufferFdLookup;
    _ = resolveBufferFdLookupReturn;
    _ = BufferFdLookupDisposition.missing_fd;
}

test "phase 8 perf-buffer poll helper keeps buffer-window lookup returns compact and mapped-size-shaped" {
    _ = summarizeBufferWindowLookup;
    _ = resolveBufferWindowLookupReturn;
    _ = BufferWindowLookupDisposition.missing_window;
}

test "resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries" {
    _ = resolvePollExecutionResultFromWaitResult;
    _ = PollError.WaitResultDisagreesWithExecutionOutcome;
    _ = PollError.WaitResultDisagreesWithReadyEventCount;
    _ = PollError.WaitResultDisagreesWithFailureCode;
}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\\nactual={failures!r}")


def run_self_test() -> int:
    base = Path(tempfile.mkdtemp(prefix="phase8-perf-buffer-poll-gate-"))
    try:
        write_text(base, SCRIPTS_README_PATH, build_scripts_readme_fixture())
        write_text(base, TESTS_README_PATH, build_tests_readme_fixture())
        write_text(base, PERF_BUFFER_POLL_TEST_PATH, build_perf_buffer_poll_test_fixture())

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        for marker in SCRIPTS_README_REQUIRED_MARKERS:
            write_text(
                base,
                SCRIPTS_README_PATH,
                build_scripts_readme_fixture().replace(marker, "", 1),
            )
            expect_failure(base, f"missing_marker:{SCRIPTS_README_PATH}:{marker}")
            write_text(base, SCRIPTS_README_PATH, build_scripts_readme_fixture())

        for marker in TESTS_README_REQUIRED_MARKERS:
            write_text(
                base,
                TESTS_README_PATH,
                build_tests_readme_fixture().replace(marker, "", 1),
            )
            expect_failure(base, f"missing_marker:{TESTS_README_PATH}:{marker}")
            write_text(base, TESTS_README_PATH, build_tests_readme_fixture())

        for marker in PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS:
            write_text(
                base,
                PERF_BUFFER_POLL_TEST_PATH,
                build_perf_buffer_poll_test_fixture().replace(marker, "", 1),
            )
            expect_failure(base, f"missing_marker:{PERF_BUFFER_POLL_TEST_PATH}:{marker}")
            write_text(base, PERF_BUFFER_POLL_TEST_PATH, build_perf_buffer_poll_test_fixture())

        shutil.rmtree(base / "scripts", ignore_errors=True)
        expect_failure(base, f"missing_file:{SCRIPTS_README_PATH}")
        write_text(base, SCRIPTS_README_PATH, build_scripts_readme_fixture())

        shutil.rmtree(base / "zigux/tests", ignore_errors=True)
        expect_failure(base, f"missing_file:{TESTS_README_PATH}")
        write_text(base, TESTS_README_PATH, build_tests_readme_fixture())
        write_text(base, PERF_BUFFER_POLL_TEST_PATH, build_perf_buffer_poll_test_fixture())

        shutil.rmtree(base / "zigux/tests", ignore_errors=True)
        write_text(base, TESTS_README_PATH, build_tests_readme_fixture())
        expect_failure(base, f"missing_file:{PERF_BUFFER_POLL_TEST_PATH}")
    finally:
        shutil.rmtree(base, ignore_errors=True)

    print("PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST=pass")
    print(
        f"PHASE8_PERF_BUFFER_POLL_GATE_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}"
    )
    print(
        f"PHASE8_PERF_BUFFER_POLL_GATE_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_TEST_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the surviving Phase 8 perf-buffer poll packet stays aligned "
            "across the scripts guide, the tests guide, and the bounded poll helper test."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=ROOT,
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
            print(f"PHASE8_PERF_BUFFER_POLL_GATE_ERROR={failure}")
        return 1

    print(
        f"PHASE8_PERF_BUFFER_POLL_GATE_SCRIPTS_README_MARKER_COUNT={len(SCRIPTS_README_REQUIRED_MARKERS)}"
    )
    print(
        f"PHASE8_PERF_BUFFER_POLL_GATE_TESTS_README_MARKER_COUNT={len(TESTS_README_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_TEST_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS)}"
    )
    print("PHASE8_PERF_BUFFER_POLL_GATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

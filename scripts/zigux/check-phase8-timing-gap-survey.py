#!/usr/bin/env python3
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase8-timing-gap-survey.py"
SURVEY_PATH = "Documentation/zigux/phase8-timing-gap-survey.md"
POLL_SLICE_PATH = "Documentation/zigux/phase8-perf-buffer-poll-slice.md"
LIBBPF_SURVEY_PATH = "Documentation/zigux/phase8-libbpf-segment-survey.md"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"
WAIT_BUDGET_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig"
MAKEFILE_PATH = "zigux/Makefile"

REQUIRED_MARKERS = {
    SURVEY_PATH: (
        "# Phase 8 Timing Gap Survey",
        "`PHASE8_STATUS=parked_gap_survey`",
        "`PHASE8_SURVEY=timing-gap-readback`",
        "roadmap anchor: `tools/lib/bpf/libbpf.c`",
        "Current `master` already keeps helper-local wait budgeting explicit through `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`.",
        "Current `master` does materialize helper-local wait-budget normalization, but it still does not materialize standalone timer helper behavior or standalone clockevent helper behavior.",
        "The remaining gap is the absence of a dedicated standalone timing helper family that would own timer or clockevent behavior outside the bounded perf-buffer poll packet.",
        "- standalone timer helper behavior",
        "- standalone clockevent helper behavior",
        "- broader timeout-sensitive routing behavior",
    ),
    POLL_SLICE_PATH: (
        "Current `master` keeps the dedicated helper packet reviewable through `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_attempt_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_fd_verify.zig`, `tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-validate`, `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `make -C zigux phase8-perf-buffer-poll-test`, and `make -C zigux phase8-test`.",
        "Current `master` now keeps helper-local wait-budget normalization explicit through `tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`, including bounded millisecond-to-nanosecond conversion for existing poll waits.",
        "The dedicated reminder still stays explicit about no standalone timer helper behavior and no standalone clockevent helper behavior.",
    ),
    LIBBPF_SURVEY_PATH: (
        "The timing-adjacent poll boundary is already explicit through `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `make -C zigux phase8-perf-buffer-poll-test`; those reminder surfaces keep the packet honest about no standalone timer or clockevent helper behavior and about no broader timeout-sensitive routing behavior.",
    ),
    PHASE8_BUILD_PATH: (
        "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
        "phase8-perf-buffer-wait-budget-tests",
        "test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);",
    ),
    WAIT_BUDGET_PATH: (
        "pub const WaitBudgetSummary = struct {",
        "bounded_timeout_ms: ?u32,",
        "bounded_timeout_ns: ?u64,",
        "pub fn summarizeWaitBudget(timeout_ms: i32)",
        "pub fn summarizeWaitBudgetFromPollSummary(summary: perf_buffer_poll.PollSummary)",
        "phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets",
        "phase8 perf-buffer wait budget rejects invalid negative waits",
    ),
    MAKEFILE_PATH: (
        "phase8-validate:",
        "phase8-perf-buffer-poll-test:",
        "phase8-test:",
    ),
}


def write_text(root: Path, rel_path: str, text: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for rel_path, markers in REQUIRED_MARKERS.items():
        path = root / rel_path
        if not path.exists():
            failures.append(f"missing_file:{rel_path}")
            continue
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_fixture(root: Path) -> None:
    script = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script)
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")


def run_self_test() -> int:
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-timing-gap-survey-") as tmp:
        root = Path(tmp)
        build_fixture(root)

        baseline = validate(root)
        if baseline:
            raise SystemExit(f"self-test baseline failed: {baseline!r}")

        for rel_path, markers in REQUIRED_MARKERS.items():
            original = read_text(root, rel_path)
            for marker in markers:
                write_text(root, rel_path, original.replace(marker, "", 1))
                expected = f"missing_marker:{rel_path}:{marker}"
                failures = validate(root)
                if expected not in failures:
                    raise SystemExit(f"expected {expected!r}, got {failures!r}")
                write_text(root, rel_path, original)
                case_count += 1

        for rel_path in REQUIRED_MARKERS:
            original = read_text(root, rel_path)
            (root / rel_path).unlink()
            expected = f"missing_file:{rel_path}"
            failures = validate(root)
            if expected not in failures:
                raise SystemExit(f"expected {expected!r}, got {failures!r}")
            write_text(root, rel_path, original)
            case_count += 1

    print("PHASE8_TIMING_GAP_SURVEY_SELF_TEST=pass")
    print(f"PHASE8_TIMING_GAP_SURVEY_SELF_TEST_CASE_COUNT={case_count}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the Phase 8 timing-gap survey stays aligned with the bounded perf-buffer timing packet."
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    failures = validate(args.root)
    if failures:
        for failure in failures:
            print(f"PHASE8_TIMING_GAP_SURVEY_ERROR={failure}")
        return 1

    print(f"PHASE8_TIMING_GAP_SURVEY_FILE_COUNT={len(REQUIRED_MARKERS)}")
    print(
        "PHASE8_TIMING_GAP_SURVEY_MARKER_COUNT="
        f"{sum(len(markers) for markers in REQUIRED_MARKERS.values())}"
    )
    print("PHASE8_TIMING_GAP_SURVEY=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_PATH = "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"
SEQUENCING_PATH = "Documentation/zigux/phase8-tooling-lane-sequencing.md"
SLICE_PATH = "Documentation/zigux/phase8-perf-buffer-poll-slice.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
REVIEW_CHECKLIST_PATH = "Documentation/zigux/review-checklist.md"
MAKEFILE_PATH = "zigux/Makefile"
PACKET_HELPER_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
PACKET_BUILD_PATH = "zigux/tests/phase8_build.zig"
PACKET_TEST_PATH = "zigux/tests/phase8_perf_buffer_poll.zig"
PACKET_ONLY_BUILD_PATH = "zigux/tests/phase8_perf_buffer_poll_only_build.zig"

REQUIRED_FILES = (
    SCRIPT_PATH,
    SEQUENCING_PATH,
    SLICE_PATH,
    SCRIPTS_README_PATH,
    TESTS_README_PATH,
    REVIEW_CHECKLIST_PATH,
    MAKEFILE_PATH,
    PACKET_HELPER_PATH,
    PACKET_BUILD_PATH,
    PACKET_TEST_PATH,
    PACKET_ONLY_BUILD_PATH,
)

REQUIRED_MARKERS = {
    SEQUENCING_PATH: (
        "Focused replay routes:",
        "make -C zigux phase8-perf-buffer-poll-test",
        "make -C zigux phase8-libbpf-segments-test",
    ),
    SLICE_PATH: (
        "PHASE8_SLICE=libbpf-perf-buffer-poll",
        "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll.zig",
        "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
        "zigux/tests/phase8_build.zig",
        "make -C zigux phase8-validate",
        "python3 scripts/zigux/validate-phase8.py --self-test",
        "python3 scripts/zigux/validate-phase8.py",
        "make -C zigux phase8-perf-buffer-poll-test",
        "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all",
        "make -C zigux phase8-test",
        "zig build test --build-file zigux/tests/phase8_build.zig --summary all",
        "make -C zigux phase8",
    ),
    SCRIPTS_README_PATH: (
        "Phase 8 flow",
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ),
    TESTS_README_PATH: (
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ),
    REVIEW_CHECKLIST_PATH: (
        "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
        "`make -C zigux phase8-perf-buffer-poll-test`",
        "`make -C zigux phase8-libbpf-segments-test`",
    ),
    MAKEFILE_PATH: (
        "scripts/zigux/check-phase8-perf-buffer-poll-gate.py",
        "phase8-perf-buffer-poll-test:",
        "phase8-libbpf-segments-test:",
    ),
    PACKET_HELPER_PATH: (
        "pub fn classifyWaitClass(",
        "pub fn summarizePollExecutionResultFromWaitResult(",
        "ReadyBufferProcessingExceedsObservedEvents",
        "test \"summarizePollExecution rejects impossible processing outside the live perf_buffer__poll wait result\" {",
        "test \"summarizePollExecution rejects processing more ready buffers than the helper counted as ready\" {",
        "test \"summarizePoll rejects impossible buffer state for timeout interrupt and failed wait results\" {",
    ),
    PACKET_TEST_PATH: (
        "test \"phase 8 perf-buffer poll docs keep the bounded wait-result helper explicit\" {",
        "test \"phase 8 perf-buffer poll helper keeps the final return-path bookkeeping below routing parity\" {",
        "test \"resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries\" {",
    ),
    PACKET_ONLY_BUILD_PATH: (
        "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
        "phase8_perf_buffer_poll.zig",
        "phase8-perf-buffer-poll-tests",
    ),
}


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    for rel_path in REQUIRED_FILES:
        if not (root / rel_path).exists():
            problems.append(f"missing-file:{rel_path}")
    if problems:
        return problems

    for rel_path, markers in REQUIRED_MARKERS.items():
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                problems.append(f"missing-marker:{rel_path}:{marker}")
    return problems


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / SCRIPT_PATH)],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_fixture_root(root: Path) -> None:
    script_text = Path(__file__).read_text(encoding="utf-8")
    write_text(root, SCRIPT_PATH, script_text)
    for rel_path, markers in REQUIRED_MARKERS.items():
        write_text(root, rel_path, "\n".join(markers) + "\n")
    for rel_path in (
        PACKET_HELPER_PATH,
        PACKET_BUILD_PATH,
        PACKET_TEST_PATH,
        PACKET_ONLY_BUILD_PATH,
    ):
        if rel_path in REQUIRED_MARKERS:
            continue
        write_text(root, rel_path, "// fixture\n")


def assert_missing_case(root: Path, rel_path: str, marker: str) -> None:
    text = read_text(root, rel_path)
    if marker not in text:
        raise SystemExit(f"self-test-fixture-missing:{rel_path}:{marker}")
    (root / rel_path).write_text(text.replace(marker, "", 1), encoding="utf-8")
    result = run_validator(root)
    expected = f"missing-marker:{rel_path}:{marker}"
    output = result.stdout.strip() or result.stderr.strip() or "no_output"
    if result.returncode == 0:
        raise SystemExit(f"self-test-unexpected-pass:{rel_path}:{marker}")
    if expected not in output:
        raise SystemExit(f"self-test-mismatch:{expected}:{output}")


def run_self_test() -> int:
    cases = 1
    with tempfile.TemporaryDirectory(prefix="zigux_phase8_perf_buffer_poll_gate_") as tmp:
        baseline_root = Path(tmp) / "baseline"
        make_fixture_root(baseline_root)
        baseline = run_validator(baseline_root)
        if baseline.returncode != 0:
            details = baseline.stdout.strip() or baseline.stderr.strip() or "no_output"
            raise SystemExit(f"self-test-baseline-failed:{details}")

        mutations = (
            (SCRIPTS_README_PATH, "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`"),
            (TESTS_README_PATH, "`make -C zigux phase8-perf-buffer-poll-test`"),
            (REVIEW_CHECKLIST_PATH, "`make -C zigux phase8-libbpf-segments-test`"),
            (SEQUENCING_PATH, "make -C zigux phase8-perf-buffer-poll-test"),
            (SLICE_PATH, "python3 scripts/zigux/validate-phase8.py --self-test"),
            (SLICE_PATH, "zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all"),
            (SLICE_PATH, "make -C zigux phase8-test"),
            (MAKEFILE_PATH, "phase8-perf-buffer-poll-test:"),
            (MAKEFILE_PATH, "scripts/zigux/check-phase8-perf-buffer-poll-gate.py"),
            (PACKET_HELPER_PATH, "pub fn summarizePollExecutionResultFromWaitResult("),
            (PACKET_HELPER_PATH, "test \"summarizePollExecution rejects impossible processing outside the live perf_buffer__poll wait result\" {"),
            (PACKET_HELPER_PATH, "test \"summarizePollExecution rejects processing more ready buffers than the helper counted as ready\" {"),
            (PACKET_HELPER_PATH, "test \"summarizePoll rejects impossible buffer state for timeout interrupt and failed wait results\" {"),
            (PACKET_TEST_PATH, "test \"phase 8 perf-buffer poll docs keep the bounded wait-result helper explicit\" {"),
            (PACKET_ONLY_BUILD_PATH, "phase8-perf-buffer-poll-tests"),
        )
        for rel_path, marker in mutations:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            assert_missing_case(case_root, rel_path, marker)
            cases += 1

        missing_files = (
            SCRIPT_PATH,
            PACKET_HELPER_PATH,
            PACKET_BUILD_PATH,
            PACKET_TEST_PATH,
            PACKET_ONLY_BUILD_PATH,
        )
        for rel_path in missing_files:
            case_root = Path(tmp) / f"case_{cases}"
            shutil.copytree(baseline_root, case_root)
            (case_root / rel_path).unlink()
            result = run_validator(case_root)
            expected = f"missing-file:{rel_path}"
            output = result.stdout.strip() or result.stderr.strip() or "no_output"
            if result.returncode == 0:
                raise SystemExit(f"self-test-unexpected-pass:{rel_path}")
            if rel_path == SCRIPT_PATH:
                if "can't open file" not in output:
                    raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            elif expected not in output:
                raise SystemExit(f"self-test-mismatch:{expected}:{output}")
            cases += 1

    print("PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST=pass")
    print(f"PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT={cases}")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    root = Path(__file__).resolve().parents[2]
    problems = validate(root)
    if problems:
        print("PHASE8_PERF_BUFFER_POLL_GATE=fail")
        print("PHASE8_PERF_BUFFER_POLL_GATE_PROBLEMS_START")
        for problem in problems:
            print(problem)
        print("PHASE8_PERF_BUFFER_POLL_GATE_PROBLEMS_END")
        return 1

    print("PHASE8_PERF_BUFFER_POLL_GATE=pass")
    print(f"PHASE8_PERF_BUFFER_POLL_GATE_ROOT={root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

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
    "Phase 8 flow - the current userspace-adjacent tooling reminder should stay anchored to the surviving perf-buffer poll packet together with the mixed-source file-path-handle bridge packet and its shipped validator and make routes, instead of reconstructing older help, kallsyms, or broader shared-bridge claims from paths that current `master` still does not serve directly",
    "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test` and `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test` replay the shipped bounded Phase 8 reminder checks",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-tests-readme-alignment.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, and `zigux/tests/phase8_build.zig` keep the current mixed-source file-path-handle bridge packet and its shipped shared-build evidence reviewable on current `master`",
    "`zigux/tests/phase8_perf_buffer_poll.zig` remains the surviving direct Phase 8 replay surface and still keeps the bounded wait-result, ready-buffer, and errno-shaped lookup packet below broader route-management or online-CPU parity claims",
    "repeated authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, and `zigux/tests/phase8_libbpf_segments.zig`, so keep those broader doc, focused-build, and shared-segment names framed as repo-reality gaps or historical packet members until a same-lane reread proves they returned on current `master`",
    "keep the current Phase 8 follow-through tied to the surviving perf-buffer-poll gate, the tests-root Phase 8 summary, the shipped file-path-handle bridge validator and helper packet, and the live shared build evidence instead of widening back into exec-cmd, help, kallsyms, or broader libbpf segment wording from older route names alone",
]

TESTS_README_REQUIRED_MARKERS = [
    "current direct-readback Phase 8 anchors:",
    "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
    "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    "`scripts/zigux/validate-phase8.py`",
    "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    "`zigux/tests/phase8_build.zig`",
    "`make -C zigux phase8-file-path-handle-bridge-test`",
    "repo-reality warning for the broader remaining Phase 8 tooling packet:",
    "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
    "`Documentation/zigux/phase8-help-slice.md`",
    "`Documentation/zigux/phase8-kallsyms-slice.md`",
    "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`zigux/tests/phase8_libbpf_segments.zig`",
    "`zigux/Makefile`",
    "keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence",
    "if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`",
]

PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS = [
    'test "phase 8 perf-buffer poll tests README keeps the current direct-readback packet explicit" {',
    'test "phase 8 perf-buffer poll scripts README keeps the surviving bridge packet explicit" {',
    '"zigux/tests/README.md"',
    '"scripts/zigux/README.md"',
    '"current direct-readback Phase 8 anchors:"',
    '"`scripts/zigux/check-phase8-tests-readme-alignment.py`"',
    '"current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:"',
    '"`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`"',
    '"`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`"',
    '"`scripts/zigux/validate-phase8.py`"',
    '"`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`"',
    '"`zigux/tests/phase8_file_path_handle_bridge.zig`"',
    '"`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`"',
    '"`zigux/tests/phase8_build.zig`"',
    '"`make -C zigux phase8-file-path-handle-bridge-test`"',
    '"repo-reality warning for the broader remaining Phase 8 tooling packet:"',
    '"`Documentation/zigux/phase8-tooling-lane-sequencing.md`"',
    '"`Documentation/zigux/phase8-help-slice.md`"',
    '"`Documentation/zigux/phase8-kallsyms-slice.md`"',
    '"`Documentation/zigux/phase8-libbpf-segment-survey.md`"',
    '"`zigux/tests/phase8_perf_buffer_poll_only_build.zig`"',
    '"`zigux/tests/phase8_libbpf_segments.zig`"',
    '"`zigux/Makefile`"',
    '"keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence"',
    '"Phase 8 flow - the current userspace-adjacent tooling reminder should stay anchored to the surviving perf-buffer poll packet together with the mixed-source file-path-handle bridge packet and its shipped validator and make routes, instead of reconstructing older help, kallsyms, or broader shared-bridge claims from paths that current `master` still does not serve directly"',
    '"`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`"',
    '"`zigux/tests/phase8_perf_buffer_poll.zig` remains the surviving direct Phase 8 replay surface"',
    '"keep the current Phase 8 follow-through tied to the surviving perf-buffer-poll gate, the tests-root Phase 8 summary, the shipped file-path-handle bridge validator and helper packet, and the live shared build evidence instead of widening back into exec-cmd, help, kallsyms, or broader libbpf segment wording from older route names alone"',
    "summarizePollExecutionResultFromWaitResult",
    "summarizeBufferFdLookup",
    "summarizeBufferWindowLookup",
    "resolveBufferFdLookupReturn",
    "resolveBufferFd(found)",
    "BufferFdLookupDisposition.found_fd",
    "resolveBufferWindowLookupReturn",
    "resolveBufferWindowMappedSize",
    "PollReturnDisposition.ready_count",
    "PollReturnDisposition.processing_failed",
    "first_process_error_index",
    "PollError.InconsistentProcessingAccountingSummary",
    "BufferFdLookupDisposition.missing_fd",
    "BufferWindowLookupDisposition.found_window",
    "BufferWindowLookupDisposition.missing_window",
    "BufferWindowLookupDisposition.invalid_index",
    "error.MissingFd",
    "error.MissingWindow",
    "error.InvalidIndex",
    "mapped_size",
    "PollError.TimeoutObservationHasReadyBuffer",
    "PollError.InterruptedObservationHasReadyBuffer",
    "PollError.FailedObservationHasBufferState",
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

- Phase 8 flow - the current userspace-adjacent tooling reminder should stay anchored to the surviving perf-buffer poll packet together with the mixed-source file-path-handle bridge packet and its shipped validator and make routes, instead of reconstructing older help, kallsyms, or broader shared-bridge claims from paths that current `master` still does not serve directly
- `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test` and `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test` replay the shipped bounded Phase 8 reminder checks
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-tests-readme-alignment.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, and `zigux/tests/phase8_build.zig` keep the current mixed-source file-path-handle bridge packet and its shipped shared-build evidence reviewable on current `master`
- `zigux/tests/phase8_perf_buffer_poll.zig` remains the surviving direct Phase 8 replay surface and still keeps the bounded wait-result, ready-buffer, and errno-shaped lookup packet below broader route-management or online-CPU parity claims
- repeated authenticated contents reads on current `master` still return missing for `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-kallsyms-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, and `zigux/tests/phase8_libbpf_segments.zig`, so keep those broader doc, focused-build, and shared-segment names framed as repo-reality gaps or historical packet members until a same-lane reread proves they returned on current `master`
- keep the current Phase 8 follow-through tied to the surviving perf-buffer-poll gate, the tests-root Phase 8 summary, the shipped file-path-handle bridge validator and helper packet, and the live shared build evidence instead of widening back into exec-cmd, help, kallsyms, or broader libbpf segment wording from older route names alone
"""


def build_tests_readme_fixture() -> str:
    return """# zigux/tests

Phase 8 review packet
  * current direct-readback Phase 8 anchors:
  * `scripts/zigux/check-phase8-tests-readme-alignment.py`
  * `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
  * `zigux/tests/phase8_perf_buffer_poll.zig`
  * `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  * current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:
  * `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
  * `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
  * `scripts/zigux/validate-phase8.py`
  * `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  * `zigux/tests/phase8_file_path_handle_bridge.zig`
  * `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  * `zigux/tests/phase8_build.zig`
  * `make -C zigux phase8-file-path-handle-bridge-test`
  * repo-reality warning for the broader remaining Phase 8 tooling packet:
  * `Documentation/zigux/phase8-tooling-lane-sequencing.md`
  * `Documentation/zigux/phase8-help-slice.md`
  * `Documentation/zigux/phase8-kallsyms-slice.md`
  * `Documentation/zigux/phase8-libbpf-segment-survey.md`
  * `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
  * `zigux/tests/phase8_libbpf_segments.zig`
  * `zigux/Makefile`
  * keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence
  * if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`
"""


def build_perf_buffer_poll_test_fixture() -> str:
    return """const std = @import(\"std\");

test \"phase 8 perf-buffer poll tests README keeps the current direct-readback packet explicit\" {
    _ = \"zigux/tests/README.md\";
    _ = \"current direct-readback Phase 8 anchors:\";
    _ = \"`scripts/zigux/check-phase8-tests-readme-alignment.py`\";
    _ = \"current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:\";
    _ = \"`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`\";
    _ = \"`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`\";
    _ = \"`scripts/zigux/validate-phase8.py`\";
    _ = \"`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`\";
    _ = \"`zigux/tests/phase8_file_path_handle_bridge.zig`\";
    _ = \"`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`\";
    _ = \"`zigux/tests/phase8_build.zig`\";
    _ = \"`make -C zigux phase8-file-path-handle-bridge-test`\";
    _ = \"repo-reality warning for the broader remaining Phase 8 tooling packet:\";
    _ = \"`Documentation/zigux/phase8-tooling-lane-sequencing.md`\";
    _ = \"`Documentation/zigux/phase8-help-slice.md`\";
    _ = \"`Documentation/zigux/phase8-kallsyms-slice.md`\";
    _ = \"`Documentation/zigux/phase8-libbpf-segment-survey.md`\";
    _ = \"`zigux/tests/phase8_perf_buffer_poll_only_build.zig`\";
    _ = \"`zigux/tests/phase8_libbpf_segments.zig`\";
    _ = \"`zigux/Makefile`\";
    _ = \"keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence\";
}

test \"phase 8 perf-buffer poll scripts README keeps the surviving bridge packet explicit\" {
    _ = \"scripts/zigux/README.md\";
    _ = \"Phase 8 flow - the current userspace-adjacent tooling reminder should stay anchored to the surviving perf-buffer poll packet together with the mixed-source file-path-handle bridge packet and its shipped validator and make routes, instead of reconstructing older help, kallsyms, or broader shared-bridge claims from paths that current `master` still does not serve directly\";
    _ = \"`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`\";
    _ = \"`zigux/tests/phase8_perf_buffer_poll.zig` remains the surviving direct Phase 8 replay surface\";
    _ = \"keep the current Phase 8 follow-through tied to the surviving perf-buffer-poll gate, the tests-root Phase 8 summary, the shipped file-path-handle bridge validator and helper packet, and the live shared build evidence instead of widening back into exec-cmd, help, kallsyms, or broader libbpf segment wording from older route names alone\";
}

test \"phase 8 perf-buffer poll helper keeps the final return-path bookkeeping below routing parity\" {
    _ = summarizePollExecutionResultFromWaitResult;
    _ = PollReturnDisposition.ready_count;
    _ = PollReturnDisposition.processing_failed;
    _ = first_process_error_index;
}

test \"phase 8 perf-buffer poll helper rejects ready waits without processing attempts\" {
    _ = PollError.InconsistentProcessingAccountingSummary;
}

test \"phase 8 perf-buffer poll helper keeps buffer-fd lookup returns compact and errno-shaped\" {
    _ = summarizeBufferFdLookup;
    _ = resolveBufferFdLookupReturn;
    _ = BufferFdLookupDisposition.missing_fd;
}

test \"phase 8 perf-buffer poll helper exposes typed fd resolution beside errno-shaped fd returns\" {
    _ = BufferFdLookupDisposition.found_fd;
    _ = resolveBufferFd(found);
    _ = error.MissingFd;
}

test \"phase 8 perf-buffer poll helper keeps buffer-window lookup returns compact and mapped-size-shaped\" {
    _ = summarizeBufferWindowLookup;
    _ = resolveBufferWindowLookupReturn;
    _ = BufferWindowLookupDisposition.missing_window;
}

test \"phase 8 perf-buffer poll exposes typed mapped-size resolution beside errno-shaped window returns\" {
    _ = resolveBufferWindowMappedSize;
    _ = BufferWindowLookupDisposition.found_window;
    _ = BufferWindowLookupDisposition.invalid_index;
    _ = mapped_size;
    _ = error.MissingWindow;
    _ = error.InvalidIndex;
}

test \"phase 8 perf-buffer poll rejects impossible post-wait buffer states\" {
    _ = PollError.TimeoutObservationHasReadyBuffer;
    _ = PollError.InterruptedObservationHasReadyBuffer;
    _ = PollError.FailedObservationHasBufferState;
}

test \"resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries\" {
    _ = resolvePollExecutionResultFromWaitResult;
    _ = PollError.WaitResultDisagreesWithExecutionOutcome;
    _ = PollError.WaitResultDisagreesWithReadyEventCount;
    _ = PollError.WaitResultDisagreesWithFailureCode;
}
"""


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


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
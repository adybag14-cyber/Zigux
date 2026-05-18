#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
from pathlib import Path

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
PERF_BUFFER_POLL_HELPER_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"

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
    "BufferFdLookupDisposition.missing_fd",
    "BufferFdLookupDisposition.invalid_index",
    "resolveBufferWindowLookupReturn",
    "resolveBufferWindowMappedSize",
    "BufferWindowLookupDisposition.found_window",
    "BufferWindowLookupDisposition.missing_window",
    "BufferWindowLookupDisposition.invalid_index",
    "found.disposition",
    "missing.disposition",
    "invalid.disposition",
    "found.mapped_size",
    "missing.mapped_size",
    "invalid.mapped_size",
    "PollReturnDisposition.ready_count",
    "PollReturnDisposition.processing_failed",
    "first_process_error_index",
    "PollError.InconsistentProcessingAccountingSummary",
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

PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS = [
    "pub const BufferFdLookupDisposition = enum {",
    "pub const BufferFdLookupSummary = struct {",
    "slot_count: usize,",
    "requested_index: usize,",
    "fd: ?i32,",
    "pub const BufferFdLookupError = error{",
    "pub fn summarizeBufferFdLookup(",
    "pub fn resolveBufferFdAtIndex(",
    "pub fn resolveBufferFd(summary: BufferFdLookupSummary) BufferFdLookupError!i32 {",
    "pub fn resolveBufferFdLookupReturn(summary: BufferFdLookupSummary) i32 {",
    "pub fn resolveBufferFdLookupReturnAtIndex(",
    "pub const BufferWindowObservation = struct {",
    "mapped_size: usize = 0,",
    "pub const BufferWindowLookupDisposition = enum {",
    "pub const BufferWindowLookupSummary = struct {",
    "mapped_size: ?usize,",
    "pub const BufferWindowLookupError = error{",
    "pub fn summarizeBufferWindowLookup(",
    "pub fn resolveBufferWindowMappedSizeAtIndex(",
    "pub fn resolveBufferWindowMappedSize(summary: BufferWindowLookupSummary) BufferWindowLookupError!usize {",
    "pub fn resolveBufferWindowLookupReturn(summary: BufferWindowLookupSummary) i32 {",
    "pub fn resolveBufferWindowLookupReturnAtIndex(",
    'test "phase8 perf-buffer poll exposes typed fd resolution beside errno-shaped fd returns" {',
    'test "phase8 perf-buffer poll resolves typed fd lookups without manual summary plumbing" {',
    'test "phase8 perf-buffer poll resolves errno-shaped fd and window lookups without manual summary plumbing" {',
    "try std.testing.expectError(error.MissingFd, resolveBufferFd(missing));",
    'test "phase8 perf-buffer poll exposes typed mapped-size resolution beside errno-shaped window returns" {',
    'test "phase8 perf-buffer poll resolves typed mapped-size lookups without manual summary plumbing" {',
    "try std.testing.expectError(error.MissingWindow, resolveBufferWindowMappedSize(missing));",
]


def read_text(root: Path, rel_path: str) -> str:
    return (root / rel_path).read_text(encoding="utf-8")


def write_text(root: Path, rel_path: str, content: str) -> None:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    required_files = (
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        PERF_BUFFER_POLL_TEST_PATH,
        PERF_BUFFER_POLL_HELPER_PATH,
    )
    for rel_path in required_files:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    marker_groups = (
        (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
        (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_TEST_PATH, PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_HELPER_PATH, PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS),
    )
    for rel_path, markers in marker_groups:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_fixture_root(root: Path) -> None:
    marker_groups = (
        (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
        (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_TEST_PATH, PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_HELPER_PATH, PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS),
    )
    for rel_path, markers in marker_groups:
        write_text(root, rel_path, "\n".join(markers) + "\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    with tempfile.TemporaryDirectory(prefix="phase8-perf-buffer-poll-gate-") as tmp:
        base = Path(tmp)
        build_fixture_root(base)

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        marker_groups = (
            (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
            (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
            (PERF_BUFFER_POLL_TEST_PATH, PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS),
            (PERF_BUFFER_POLL_HELPER_PATH, PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS),
        )
        for rel_path, markers in marker_groups:
            baseline = "\n".join(markers) + "\n"
            for marker in markers:
                write_text(base, rel_path, baseline.replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")
                write_text(base, rel_path, baseline)

        for rel_path in (
            SCRIPTS_README_PATH,
            TESTS_README_PATH,
            PERF_BUFFER_POLL_TEST_PATH,
            PERF_BUFFER_POLL_HELPER_PATH,
        ):
            path = base / rel_path
            original = path.read_text(encoding="utf-8")
            path.unlink()
            expect_failure(base, f"missing_file:{rel_path}")
            write_text(base, rel_path, original)

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
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_HELPER_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the surviving Phase 8 perf-buffer poll packet stays aligned "
            "across the scripts guide, the tests guide, the bounded poll helper test, "
            "and the helper source markers."
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
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_HELPER_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS)}"
    )
    print("PHASE8_PERF_BUFFER_POLL_GATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

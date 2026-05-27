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
NOTE_PATH = "Documentation/zigux/phase8-perf-buffer-poll-slice.md"
BRIDGE_BOUNDARY_PATH = "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md"
SCRIPTS_README_PATH = "scripts/zigux/README.md"
TESTS_README_PATH = "zigux/tests/README.md"
PERF_BUFFER_POLL_TEST_PATH = "zigux/tests/phase8_perf_buffer_poll.zig"
PERF_BUFFER_POLL_BUILD_PATH = "zigux/tests/phase8_perf_buffer_poll_only_build.zig"
PERF_BUFFER_POLL_HELPER_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"
PERF_BUFFER_WAIT_BUDGET_HELPER_PATH = "tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig"
PHASE8_BUILD_PATH = "zigux/tests/phase8_build.zig"

NOTE_REQUIRED_MARKERS = [
    "# Phase 8 Perf-Buffer Poll Slice",
    "`PHASE8_STATUS=parked_helper_slice`",
    "`PHASE8_SLICE=libbpf-perf-buffer-poll`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`",
    "`tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`zigux/tests/phase8_build.zig`",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "`make -C zigux phase8-validate`",
    "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
    "`make -C zigux phase8-test`",
    "no standalone timer helper behavior",
    "no standalone clockevent helper behavior",
    "broader perf-buffer-online-cpu-routing parity",
]

BRIDGE_BOUNDARY_REQUIRED_MARKERS = [
    "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
    "authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.",
    "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `zigux/tests/phase8_file_path_handle_bridge.zig` directly",
    "`python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "no standalone timer helper behavior",
    "no standalone clockevent helper behavior",
    "no broader timeout-sensitive routing behavior",
]

SCRIPTS_README_REQUIRED_MARKERS = [
    "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit beside the surviving perf-buffer poll packet and the mixed-source file-path-handle bridge packet, while treating the returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-tests-readme-alignment.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the mixed-source file-path-handle bridge packet explicit on current `master` beside the surviving perf-buffer poll route",
]

TESTS_README_REQUIRED_MARKERS = [
    "current direct-readback Phase 8 anchors:",
    "`scripts/zigux/check-phase8-tests-readme-alignment.py`",
    "`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`",
    "`zigux/tests/phase8_exec_cmd.zig`",
    "`zigux/tests/phase8_exec_cmd_only_build.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
    "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    "`scripts/zigux/validate-phase8.py`",
    "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`",
    "`zigux/tests/phase8_file_path_handle_boundary_guard.zig`",
    "`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`",
    "`zigux/tests/phase8_build.zig`",
    "`make -C zigux phase8-exec-cmd-test`",
    "`make -C zigux phase8-file-path-handle-bridge-test`",
    "current `zigux/tests/phase8_build.zig` also keeps the landed boundary-guard and manifest-sync witnesses inside the shared aggregate replay, so this tests-root reminder should treat both checks as current current-`master` evidence instead of leaving them implied only by the aggregate build route",
    "repo-reality warning for the broader remaining Phase 8 tooling packet:",
    "`Documentation/zigux/phase8-libbpf-segment-survey.md`",
    "`Documentation/zigux/phase8-tooling-lane-sequencing.md`",
    "`Documentation/zigux/phase8-help-slice.md`",
    "`Documentation/zigux/phase8-kallsyms-slice.md`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`zigux/tests/phase8_libbpf_segments.zig`",
    "`zigux/Makefile`",
    "current public-tree rereads now rematerialize the broader help, kallsyms, and libbpf-segment companions on `master`, so treat those returned paths as public-tree-backed broader packet evidence rather than as part of the narrow direct-readback anchor set",
    "keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence",
    "if future same-lane work rematerializes the remaining broader docs, focused perf-buffer build shard, shared libbpf segment replay, or Makefile routes, or changes the focused bridge shard, the shared build replay, or the libbpf segment review packet, refresh this tests-root summary only after rereading the current direct-readback anchors together with the mixed-source file-path-handle bridge packet on current `master`",
]

PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
    "perf_buffer_wait_budget_module.addImport(\"perf_buffer_poll\", perf_buffer_poll_module);",
    "phase8-perf-buffer-wait-budget-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig",
    "phase8-perf-buffer-poll-verify-tests",
    "test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
    "test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);",
]

PHASE8_BUILD_REQUIRED_MARKERS = [
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
    "perf_buffer_wait_budget_module.addImport(\"perf_buffer_poll\", perf_buffer_poll_module);",
    "phase8-perf-buffer-wait-budget-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    "test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
]

PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS = [
    'test "phase 8 perf-buffer poll tests README keeps the current direct-readback packet explicit" {',
    'test "phase 8 perf-buffer poll scripts README keeps the current bridge packet explicit" {',
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
    '"`zigux/tests/phase8_file_path_handle_boundary_guard.zig`"',
    '"`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`"',
    '"`zigux/tests/phase8_build.zig`"',
    '"`make -C zigux phase8-file-path-handle-bridge-test`"',
    '"current `zigux/tests/phase8_build.zig` also keeps the landed boundary-guard and manifest-sync witnesses inside the shared aggregate replay, so this tests-root reminder should treat both checks as current current-`master` evidence instead of leaving them implied only by the aggregate build route"',
    '"repo-reality warning for the broader remaining Phase 8 tooling packet:"',
    '"`Documentation/zigux/phase8-tooling-lane-sequencing.md`"',
    '"`Documentation/zigux/phase8-help-slice.md`"',
    '"`Documentation/zigux/phase8-kallsyms-slice.md`"',
    '"`zigux/tests/phase8_perf_buffer_poll_only_build.zig`"',
    '"`zigux/tests/phase8_libbpf_segments.zig`"',
    '"`zigux/Makefile`"',
    '"keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence"',
    '"Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit beside the surviving perf-buffer poll packet and the mixed-source file-path-handle bridge packet, while treating the returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors"',
    '"`scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-tests-readme-alignment.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root"',
    '"`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the mixed-source file-path-handle bridge packet explicit on current `master` beside the surviving perf-buffer poll route"',
    'test "phase 8 perf-buffer poll helper keeps direct ready-buffer attempt wrappers aligned" {',
    'test "phase 8 perf-buffer poll helper resolves ready-buffer fd lookups without slot plumbing" {',
    'test "phase 8 perf-buffer poll helper keeps ready-buffer fd lookup returns compact and errno-shaped" {',
    'test "phase 8 perf-buffer poll helper resolves ready-buffer mapped-window lookups without manual slot plumbing" {',
    'test "phase 8 perf-buffer poll helper keeps ready-buffer window lookup returns errno-shaped" {',
    'test "resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries" {',
    "resolveReadyBufferAttemptAtIndex",
    "resolveReadyBufferAttemptIndexReturn",
    "resolveReadyBufferFdAtAttempt",
    "resolveReadyBufferFdLookupReturnAtAttempt",
    "resolveReadyBufferWindowMappedSizeAtAttempt",
    "resolveReadyBufferWindowLookupReturnAtAttempt",
    "short_fds",
    "short_windows",
    "error.MissingReadyBuffer",
    "error.InvalidIndex",
    "error.MissingFd",
    "error.MissingWindow",
    "summarizePollExecutionResultFromWaitResult",
    "resolvePollExecutionResultFromWaitResult",
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
    "mapped_size",
    "PollError.TimeoutObservationHasReadyBuffer",
    "PollError.InterruptedObservationHasReadyBuffer",
    "PollError.FailedObservationHasBufferState",
    "PollError.WaitResultDisagreesWithExecutionOutcome",
    "PollError.WaitResultDisagreesWithReadyEventCount",
    "PollError.WaitResultDisagreesWithFailureCode",
]

PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS = [
    "pub const ReadyBufferAttemptLookupDisposition = enum {",
    "pub const ReadyBufferAttemptLookupSummary = struct {",
    "requested_attempt_index: usize,",
    "ready_index: ?usize,",
    "ready_count: usize,",
    "pub const ReadyBufferAttemptLookupError = error{",
    "pub fn summarizeReadyBufferAttemptLookup(",
    "pub fn resolveReadyBufferAttemptLookup(",
    "pub fn resolveReadyBufferAttemptAtIndex(",
    "pub fn resolveReadyBufferAttemptIndexReturn(",
    "pub fn resolveReadyBufferAttemptLookupReturn(",
    "pub const BufferFdLookupDisposition = enum {",
    "pub const BufferFdLookupSummary = struct {",
    "slot_count: usize,",
    "requested_index: usize,",
    "fd: ?i32,",
    "pub const BufferFdLookupError = error{",
    "pub const ReadyBufferFdLookupError = ReadyBufferAttemptLookupError || BufferFdLookupError;",
    "pub fn summarizeBufferFdLookup(",
    "pub fn resolveBufferFdAtIndex(",
    "pub fn resolveBufferFd(summary: BufferFdLookupSummary) BufferFdLookupError!i32 {",
    "pub fn resolveBufferFdLookupReturn(summary: BufferFdLookupSummary) i32 {",
    "pub fn resolveBufferFdLookupReturnAtIndex(",
    "pub fn resolveReadyBufferFdAtAttempt(",
    "pub fn resolveReadyBufferFdLookupReturnAtAttempt(",
    "pub const BufferWindowObservation = struct {",
    "mapped_size: usize = 0,",
    "pub const BufferWindowLookupDisposition = enum {",
    "pub const BufferWindowLookupSummary = struct {",
    "mapped_size: ?usize,",
    "pub const BufferWindowLookupError = error{",
    "pub const ReadyBufferWindowLookupError = ReadyBufferAttemptLookupError || BufferWindowLookupError;",
    "pub fn summarizeBufferWindowLookup(",
    "pub fn resolveBufferWindowMappedSizeAtIndex(",
    "pub fn resolveBufferWindowMappedSize(summary: BufferWindowLookupSummary) BufferWindowLookupError!usize {",
    "pub fn resolveBufferWindowLookupReturn(summary: BufferWindowLookupSummary) i32 {",
    "pub fn resolveBufferWindowLookupReturnAtIndex(",
    "pub fn resolveReadyBufferWindowMappedSizeAtAttempt(",
    "pub fn resolveReadyBufferWindowLookupReturnAtAttempt(",
    'test "phase8 perf-buffer poll resolves ready-buffer attempt ordinals back to slot indexes" {',
    'test "phase8 perf-buffer poll exposes typed ready-buffer attempt lookup summaries" {',
    'test "phase8 perf-buffer poll resolves typed ready-buffer attempts without manual summary plumbing" {',
    'test "phase8 perf-buffer poll keeps ready-buffer attempt lookup returns errno-shaped" {',
    'test "phase8 perf-buffer poll resolves ready-buffer attempt returns without manual summary plumbing" {',
    'test "phase8 perf-buffer poll fails closed when a hand-built ready-buffer lookup index exceeds i32" {',
    'test "phase8 perf-buffer poll resolves ready-buffer fd lookups without manual slot plumbing" {',
    'test "phase8 perf-buffer poll keeps ready-buffer fd lookup returns errno-shaped" {',
    'test "phase8 perf-buffer poll exposes typed fd resolution beside errno-shaped fd returns" {',
    'test "phase8 perf-buffer poll resolves typed fd lookups without manual summary plumbing" {',
    'test "phase8 perf-buffer poll resolves ready-buffer mapped-window lookups without manual slot plumbing" {',
    'test "phase8 perf-buffer poll keeps ready-buffer window lookup returns errno-shaped" {',
    'test "phase8 perf-buffer poll resolves errno-shaped fd and window lookups without manual summary plumbing" {',
    "try std.testing.expectError(error.MissingFd, resolveBufferFd(missing));",
    'test "phase8 perf-buffer poll exposes typed mapped-size resolution beside errno-shaped window returns" {',
    'test "phase8 perf-buffer poll resolves typed mapped-size lookups without manual summary plumbing" {',
    "try std.testing.expectError(error.MissingWindow, resolveBufferWindowMappedSize(missing));",
    'test "phase8 perf-buffer poll keeps ready-count return semantics and process totals separate" {',
    'test "phase8 perf-buffer poll keeps the first processing failure tied to the ready-buffer slot" {',
    'test "phase8 perf-buffer poll turns error-only ready-event observations into buffer-state failures" {',
    'test "phase8 perf-buffer poll rejects impossible hand-built timeout summaries" {',
    'test "phase8 perf-buffer poll rejects impossible hand-built failed summaries" {',
    'test "phase8 perf-buffer poll rejects hand-built failures that point before the first ready slot" {',
    'test "phase8 perf-buffer poll rejects later failures that still point at the first ready slot" {',
    'test "phase8 perf-buffer poll lookup summaries keep slot metadata exact" {',
    "PollReturnDisposition.buffer_state_failed",
    "first_process_error_ready_index",
    "PollError.InconsistentPollSummary",
]

PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS = [
    "pub const WaitBudgetSummary = struct {",
    "timeout_ms: i32,",
    "bounded_timeout_ms: ?u32,",
    "bounded_timeout_ns: ?u64,",
    "pub fn summarizeWaitBudget(timeout_ms: i32) perf_buffer_poll.PollError!WaitBudgetSummary {",
    "pub fn summarizeWaitBudgetFromPollSummary(summary: perf_buffer_poll.PollSummary) WaitBudgetSummary {",
    'test "phase8 perf-buffer wait budget keeps nonblocking waits budgetless" {',
    'test "phase8 perf-buffer wait budget keeps indefinite waits budgetless" {',
    'test "phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets" {',
    'test "phase8 perf-buffer wait budget preserves large bounded waits without overflow" {',
    'test "phase8 perf-buffer wait budget rejects invalid negative waits" {',
    "std.time.ns_per_ms",
    "perf_buffer_poll.PollError.InvalidTimeout",
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
        NOTE_PATH,
        BRIDGE_BOUNDARY_PATH,
        SCRIPTS_README_PATH,
        TESTS_README_PATH,
        PERF_BUFFER_POLL_TEST_PATH,
        PERF_BUFFER_POLL_BUILD_PATH,
        PERF_BUFFER_POLL_HELPER_PATH,
        PERF_BUFFER_WAIT_BUDGET_HELPER_PATH,
        PHASE8_BUILD_PATH,
    )
    for rel_path in required_files:
        if not (root / rel_path).exists():
            failures.append(f"missing_file:{rel_path}")
    if failures:
        return failures

    marker_groups = (
        (NOTE_PATH, NOTE_REQUIRED_MARKERS),
        (BRIDGE_BOUNDARY_PATH, BRIDGE_BOUNDARY_REQUIRED_MARKERS),
        (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
        (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_TEST_PATH, PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_BUILD_PATH, PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_HELPER_PATH, PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS),
        (PERF_BUFFER_WAIT_BUDGET_HELPER_PATH, PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS),
        (PHASE8_BUILD_PATH, PHASE8_BUILD_REQUIRED_MARKERS),
    )
    for rel_path, markers in marker_groups:
        text = read_text(root, rel_path)
        for marker in markers:
            if marker not in text:
                failures.append(f"missing_marker:{rel_path}:{marker}")
    return failures


def build_fixture_root(root: Path) -> None:
    marker_groups = (
        (NOTE_PATH, NOTE_REQUIRED_MARKERS),
        (BRIDGE_BOUNDARY_PATH, BRIDGE_BOUNDARY_REQUIRED_MARKERS),
        (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
        (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_TEST_PATH, PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_BUILD_PATH, PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS),
        (PERF_BUFFER_POLL_HELPER_PATH, PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS),
        (PERF_BUFFER_WAIT_BUDGET_HELPER_PATH, PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS),
        (PHASE8_BUILD_PATH, PHASE8_BUILD_REQUIRED_MARKERS),
    )
    for rel_path, markers in marker_groups:
        write_text(root, rel_path, "\n".join(markers) + "\n")


def expect_failure(root: Path, expected: str) -> None:
    failures = validate(root)
    if expected not in failures:
        raise SystemExit(f"expected failure not found: {expected}\nactual={failures!r}")


def run_self_test() -> int:
    case_count = 1
    with tempfile.TemporaryDirectory(prefix="phase8-perf-buffer-poll-gate-") as tmp:
        base = Path(tmp)
        build_fixture_root(base)

        failures = validate(base)
        if failures:
            raise SystemExit(f"fixture tree should pass but failed: {failures!r}")

        marker_groups = (
            (NOTE_PATH, NOTE_REQUIRED_MARKERS),
            (BRIDGE_BOUNDARY_PATH, BRIDGE_BOUNDARY_REQUIRED_MARKERS),
            (SCRIPTS_README_PATH, SCRIPTS_README_REQUIRED_MARKERS),
            (TESTS_README_PATH, TESTS_README_REQUIRED_MARKERS),
            (PERF_BUFFER_POLL_TEST_PATH, PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS),
            (PERF_BUFFER_POLL_BUILD_PATH, PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS),
            (PERF_BUFFER_POLL_HELPER_PATH, PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS),
            (PERF_BUFFER_WAIT_BUDGET_HELPER_PATH, PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS),
            (PHASE8_BUILD_PATH, PHASE8_BUILD_REQUIRED_MARKERS),
        )
        for rel_path, markers in marker_groups:
            baseline = "\n".join(markers) + "\n"
            for marker in markers:
                write_text(base, rel_path, baseline.replace(marker, ""))
                expect_failure(base, f"missing_marker:{rel_path}:{marker}")
                write_text(base, rel_path, baseline)
                case_count += 1

        for rel_path in (
            NOTE_PATH,
            BRIDGE_BOUNDARY_PATH,
            SCRIPTS_README_PATH,
            TESTS_README_PATH,
            PERF_BUFFER_POLL_TEST_PATH,
            PERF_BUFFER_POLL_BUILD_PATH,
            PERF_BUFFER_POLL_HELPER_PATH,
            PERF_BUFFER_WAIT_BUDGET_HELPER_PATH,
            PHASE8_BUILD_PATH,
        ):
            path = base / rel_path
            original = path.read_text(encoding="utf-8")
            path.unlink()
            expect_failure(base, f"missing_file:{rel_path}")
            write_text(base, rel_path, original)
            case_count += 1

    print("PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST=pass")
    print(f"PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST_CASE_COUNT={case_count}")
    print(f"PHASE8_PERF_BUFFER_POLL_GATE_NOTE_MARKER_COUNT={len(NOTE_REQUIRED_MARKERS)}")
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_BRIDGE_BOUNDARY_MARKER_COUNT="
        f"{len(BRIDGE_BOUNDARY_REQUIRED_MARKERS)}"
    )
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
        "PHASE8_PERF_BUFFER_POLL_GATE_BUILD_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_HELPER_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_WAIT_BUDGET_HELPER_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_SHARED_BUILD_MARKER_COUNT="
        f"{len(PHASE8_BUILD_REQUIRED_MARKERS)}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Check that the surviving Phase 8 perf-buffer poll packet stays aligned "
            "across the dedicated poll note, the bridge-boundary reminder, the scripts guide, "
            "the tests guide, the focused poll build shard, the shared Phase 8 aggregate build, "
            "the bounded poll helper test, the wait-budget helper, and the helper source markers."
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

    print(f"PHASE8_PERF_BUFFER_POLL_GATE_NOTE_MARKER_COUNT={len(NOTE_REQUIRED_MARKERS)}")
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_BRIDGE_BOUNDARY_MARKER_COUNT="
        f"{len(BRIDGE_BOUNDARY_REQUIRED_MARKERS)}"
    )
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
        "PHASE8_PERF_BUFFER_POLL_GATE_BUILD_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_HELPER_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_WAIT_BUDGET_HELPER_FILE_MARKER_COUNT="
        f"{len(PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS)}"
    )
    print(
        "PHASE8_PERF_BUFFER_POLL_GATE_SHARED_BUILD_MARKER_COUNT="
        f"{len(PHASE8_BUILD_REQUIRED_MARKERS)}"
    )
    print("PHASE8_PERF_BUFFER_POLL_GATE=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

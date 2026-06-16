const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE8_PERF_BUFFER_POLL_GATE=pass";
pub const self_test_pass_marker = "PHASE8_PERF_BUFFER_POLL_GATE_SELF_TEST=pass";

const NOTE_PATH = [_][]const u8{
    "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
};

const BRIDGE_BOUNDARY_PATH = [_][]const u8{
    "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
};

const SCRIPTS_README_PATH = [_][]const u8{
    "scripts/zigux/README.md",
};

const TESTS_README_PATH = [_][]const u8{
    "zigux/tests/README.md",
};

const PERF_BUFFER_POLL_TEST_PATH = [_][]const u8{
    "zigux/tests/phase8_perf_buffer_poll.zig",
};

const PERF_BUFFER_POLL_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_perf_buffer_poll_only_build.zig",
};

const PERF_BUFFER_POLL_HELPER_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
};

const PERF_BUFFER_WAIT_BUDGET_HELPER_PATH = [_][]const u8{
    "tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
};

const PHASE8_BUILD_PATH = [_][]const u8{
    "zigux/tests/phase8_build.zig",
};

const NOTE_REQUIRED_MARKERS = [_][]const u8{
    "# Phase 8 Perf-Buffer Poll Slice",
    "`PHASE8_STATUS=parked_helper_slice`",
    "`PHASE8_SLICE=libbpf-perf-buffer-poll`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig`",
    "`tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig`",
    "`tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`zigux/tests/phase8_perf_buffer_poll_only_build.zig`",
    "`zigux/tests/phase8_build.zig`",
    "`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`",
    "`make -C zigux phase8-validate`",
    "`zig run scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`",
    "`make -C zigux phase8-perf-buffer-poll-test`",
    "`make -C zigux phase8-test`",
    "no standalone timer helper behavior",
    "no standalone clockevent helper behavior",
    "broader perf-buffer-online-cpu-routing parity",
};

const BRIDGE_BOUNDARY_REQUIRED_MARKERS = [_][]const u8{
    "`Documentation/zigux/phase8-perf-buffer-poll-slice.md`",
    "authenticated contents readback now reaches the bridge-side helper and witness files directly again in this runtime.",
    "`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, and `zigux/tests/phase8_file_path_handle_bridge.zig` directly",
    "`zig run scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`",
    "no standalone timer helper behavior",
    "no standalone clockevent helper behavior",
    "no broader timeout-sensitive routing behavior",
};

const SCRIPTS_README_REQUIRED_MARKERS = [_][]const u8{
    "Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit beside the surviving perf-buffer poll packet and the mixed-source file-path-handle bridge packet, while treating the returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors",
    "`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`, `scripts\\zigux/check_phase8_tests_readme_alignment.zig`, `scripts\\zigux/validate_phase8.zig`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts\\zigux/validate_phase8.zig`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the mixed-source file-path-handle bridge packet explicit on current `master` beside the surviving perf-buffer poll route",
};

const TESTS_README_REQUIRED_MARKERS = [_][]const u8{
    "current direct-readback Phase 8 anchors:",
    "`scripts\\zigux/check_phase8_tests_readme_alignment.zig`",
    "`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`",
    "`zigux/tests/phase8_exec_cmd.zig`",
    "`zigux/tests/phase8_exec_cmd_only_build.zig`",
    "`zigux/tests/phase8_perf_buffer_poll.zig`",
    "`tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`",
    "current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:",
    "`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`",
    "`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`",
    "`scripts\\zigux/validate_phase8.zig`",
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
};

const PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
    "perf_buffer_wait_budget_module.addImport(\"perf_buffer_poll\", perf_buffer_poll_module);",
    "phase8-perf-buffer-wait-budget-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig",
    "phase8-perf-buffer-ready-window-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_window_verify.zig",
    "phase8-ready-buffer-window-verify-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig",
    "phase8-perf-buffer-poll-verify-tests",
    "test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
    "test_step.dependOn(&run_perf_buffer_ready_window_tests.step);",
    "test_step.dependOn(&run_ready_buffer_window_verify_tests.step);",
    "test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);",
};

const PHASE8_BUILD_REQUIRED_MARKERS = [_][]const u8{
    "../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig",
    "phase8-perf-buffer-poll-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig",
    "perf_buffer_wait_budget_module.addImport(\"perf_buffer_poll\", perf_buffer_poll_module);",
    "phase8-perf-buffer-wait-budget-tests",
    "../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig",
    "phase8-ready-buffer-fd-lookup-tests",
    "../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig",
    "phase8-perf-buffer-ready-window-tests",
    "test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);",
    "test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);",
    "test_step.dependOn(&run_perf_buffer_ready_window_tests.step);",
};

const PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS = [_][]const u8{
    "test \"phase 8 perf-buffer poll tests README keeps the current direct-readback packet explicit\" {",
    "test \"phase 8 perf-buffer poll scripts README keeps the current bridge packet explicit\" {",
    "\"zigux/tests/README.md\"",
    "\"scripts/zigux/README.md\"",
    "\"current direct-readback Phase 8 anchors:\"",
    "\"`scripts\\zigux/check_phase8_tests_readme_alignment.zig`\"",
    "\"current mixed-source file-path-handle bridge companions also remain reviewable on current `master` through the public tree and aligned reminder packet:\"",
    "\"`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`\"",
    "\"`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`\"",
    "\"`scripts\\zigux/validate_phase8.zig`\"",
    "\"`tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`\"",
    "\"`zigux/tests/phase8_file_path_handle_bridge.zig`\"",
    "\"`zigux/tests/phase8_file_path_handle_bridge_only_build.zig`\"",
    "\"`zigux/tests/phase8_file_path_handle_boundary_guard.zig`\"",
    "\"`zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`\"",
    "\"`zigux/tests/phase8_build.zig`\"",
    "\"`make -C zigux phase8-file-path-handle-bridge-test`\"",
    "\"current `zigux/tests/phase8_build.zig` also keeps the landed boundary-guard and manifest-sync witnesses inside the shared aggregate replay, so this tests-root reminder should treat both checks as current current-`master` evidence instead of leaving them implied only by the aggregate build route\"",
    "\"repo-reality warning for the broader remaining Phase 8 tooling packet:\"",
    "\"`Documentation/zigux/phase8-tooling-lane-sequencing.md`\"",
    "\"`Documentation/zigux/phase8-help-slice.md`\"",
    "\"`Documentation/zigux/phase8-kallsyms-slice.md`\"",
    "\"`zigux/tests/phase8_perf_buffer_poll_only_build.zig`\"",
    "\"`zigux/tests/phase8_libbpf_segments.zig`\"",
    "\"`zigux/Makefile`\"",
    "\"keep the narrower current Phase 8 reminder tied to the directly readable tests-readme checker plus the surviving perf-buffer poll checker, helper, and focused test packet, while also keeping the landed mixed-source file-path-handle bridge packet visible through the shared bridge-boundary survey, bridge slice, validator entrypoint, focused bridge proof, and helper-local replay instead of treating that same-lane bridge surface as missing current-master evidence\"",
    "\"Phase 8 flow - the current userspace-adjacent tooling reminder should keep the direct exec-cmd command packet explicit beside the surviving perf-buffer poll packet and the mixed-source file-path-handle bridge packet, while treating the returned help, kallsyms, and broader libbpf-segment companions as public-tree-backed broader packet evidence instead of as missing routes or direct scripts-root anchors\"",
    "\"`scripts\\zigux/check_phase8_perf_buffer_poll_gate.zig`, `scripts\\zigux/check_phase8_tests_readme_alignment.zig`, `scripts\\zigux/validate_phase8.zig`, `zigux/tests/README.md`, and `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` keep the directly readable checker, validator, tests-root reminder, helper, and focused perf-buffer packet explicit from the scripts root\"",
    "\"`Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts\\zigux/validate_phase8.zig`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` keep the mixed-source file-path-handle bridge packet explicit on current `master` beside the surviving perf-buffer poll route\"",
    "test \"phase 8 perf-buffer poll helper keeps direct ready-buffer attempt wrappers aligned\" {",
    "test \"phase 8 perf-buffer poll helper resolves ready-buffer fd lookups without slot plumbing\" {",
    "test \"phase 8 perf-buffer poll helper keeps ready-buffer fd lookup returns compact and errno-shaped\" {",
    "test \"phase 8 perf-buffer poll helper resolves ready-buffer mapped-window lookups without manual slot plumbing\" {",
    "test \"phase 8 perf-buffer poll helper keeps ready-buffer window lookup returns errno-shaped\" {",
    "test \"resolvePollExecutionResultFromWaitResult rejects mismatched wait-result and execution summaries\" {",
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
};

const PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS = [_][]const u8{
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
    "test \"phase8 perf-buffer poll resolves ready-buffer attempt ordinals back to slot indexes\" {",
    "test \"phase8 perf-buffer poll exposes typed ready-buffer attempt lookup summaries\" {",
    "test \"phase8 perf-buffer poll resolves typed ready-buffer attempts without manual summary plumbing\" {",
    "test \"phase8 perf-buffer poll keeps ready-buffer attempt lookup returns errno-shaped\" {",
    "test \"phase8 perf-buffer poll resolves ready-buffer attempt returns without manual summary plumbing\" {",
    "test \"phase8 perf-buffer poll fails closed when a hand-built ready-buffer lookup index exceeds i32\" {",
    "test \"phase8 perf-buffer poll resolves ready-buffer fd lookups without manual slot plumbing\" {",
    "test \"phase8 perf-buffer poll keeps ready-buffer fd lookup returns errno-shaped\" {",
    "test \"phase8 perf-buffer poll exposes typed fd resolution beside errno-shaped fd returns\" {",
    "test \"phase8 perf-buffer poll resolves typed fd lookups without manual summary plumbing\" {",
    "test \"phase8 perf-buffer poll resolves ready-buffer mapped-window lookups without manual slot plumbing\" {",
    "test \"phase8 perf-buffer poll keeps ready-buffer window lookup returns errno-shaped\" {",
    "test \"phase8 perf-buffer poll resolves errno-shaped fd and window lookups without manual summary plumbing\" {",
    "try std.testing.expectError(error.MissingFd, resolveBufferFd(missing));",
    "test \"phase8 perf-buffer poll exposes typed mapped-size resolution beside errno-shaped window returns\" {",
    "test \"phase8 perf-buffer poll resolves typed mapped-size lookups without manual summary plumbing\" {",
    "try std.testing.expectError(error.MissingWindow, resolveBufferWindowMappedSize(missing));",
    "test \"phase8 perf-buffer poll keeps ready-count return semantics and process totals separate\" {",
    "test \"phase8 perf-buffer poll keeps the first processing failure tied to the ready-buffer slot\" {",
    "test \"phase8 perf-buffer poll turns error-only ready-event observations into buffer-state failures\" {",
    "test \"phase8 perf-buffer poll rejects impossible hand-built timeout summaries\" {",
    "test \"phase8 perf-buffer poll rejects impossible hand-built failed summaries\" {",
    "test \"phase8 perf-buffer poll rejects hand-built failures that point before the first ready slot\" {",
    "test \"phase8 perf-buffer poll rejects later failures that still point at the first ready slot\" {",
    "test \"phase8 perf-buffer poll lookup summaries keep slot metadata exact\" {",
    "PollReturnDisposition.buffer_state_failed",
    "first_process_error_ready_index",
    "PollError.InconsistentPollSummary",
};

const PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS = [_][]const u8{
    "pub const WaitBudgetSummary = struct {",
    "timeout_ms: i32,",
    "bounded_timeout_ms: ?u32,",
    "bounded_timeout_ns: ?u64,",
    "pub fn summarizeWaitBudget(timeout_ms: i32) perf_buffer_poll.PollError!WaitBudgetSummary {",
    "pub fn summarizeWaitBudgetFromPollSummary(summary: perf_buffer_poll.PollSummary) WaitBudgetSummary {",
    "test \"phase8 perf-buffer wait budget keeps nonblocking waits budgetless\" {",
    "test \"phase8 perf-buffer wait budget keeps indefinite waits budgetless\" {",
    "test \"phase8 perf-buffer wait budget normalizes bounded waits into ms and ns budgets\" {",
    "test \"phase8 perf-buffer wait budget preserves large bounded waits without overflow\" {",
    "test \"phase8 perf-buffer wait budget rejects invalid negative waits\" {",
    "std.time.ns_per_ms",
    "perf_buffer_poll.PollError.InvalidTimeout",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_note_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_note_path_path);
    const text_note_path = try guard.readUtf8File(io, allocator, text_note_path_path);
    defer allocator.free(text_note_path);
    for (NOTE_PATH) |marker| try guard.requireMarker(text_note_path, marker);
    const text_bridge_boundary_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_bridge_boundary_path_path);
    const text_bridge_boundary_path = try guard.readUtf8File(io, allocator, text_bridge_boundary_path_path);
    defer allocator.free(text_bridge_boundary_path);
    for (BRIDGE_BOUNDARY_PATH) |marker| try guard.requireMarker(text_bridge_boundary_path, marker);
    const text_scripts_readme_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_scripts_readme_path_path);
    const text_scripts_readme_path = try guard.readUtf8File(io, allocator, text_scripts_readme_path_path);
    defer allocator.free(text_scripts_readme_path);
    for (SCRIPTS_README_PATH) |marker| try guard.requireMarker(text_scripts_readme_path, marker);
    const text_tests_readme_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_tests_readme_path_path);
    const text_tests_readme_path = try guard.readUtf8File(io, allocator, text_tests_readme_path_path);
    defer allocator.free(text_tests_readme_path);
    for (TESTS_README_PATH) |marker| try guard.requireMarker(text_tests_readme_path, marker);
    const text_perf_buffer_poll_test_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_poll_test_path_path);
    const text_perf_buffer_poll_test_path = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_test_path_path);
    defer allocator.free(text_perf_buffer_poll_test_path);
    for (PERF_BUFFER_POLL_TEST_PATH) |marker| try guard.requireMarker(text_perf_buffer_poll_test_path, marker);
    const text_perf_buffer_poll_build_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_poll_build_path_path);
    const text_perf_buffer_poll_build_path = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_build_path_path);
    defer allocator.free(text_perf_buffer_poll_build_path);
    for (PERF_BUFFER_POLL_BUILD_PATH) |marker| try guard.requireMarker(text_perf_buffer_poll_build_path, marker);
    const text_perf_buffer_poll_helper_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_poll_helper_path_path);
    const text_perf_buffer_poll_helper_path = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_helper_path_path);
    defer allocator.free(text_perf_buffer_poll_helper_path);
    for (PERF_BUFFER_POLL_HELPER_PATH) |marker| try guard.requireMarker(text_perf_buffer_poll_helper_path, marker);
    const text_perf_buffer_wait_budget_helper_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_wait_budget_helper_path_path);
    const text_perf_buffer_wait_budget_helper_path = try guard.readUtf8File(io, allocator, text_perf_buffer_wait_budget_helper_path_path);
    defer allocator.free(text_perf_buffer_wait_budget_helper_path);
    for (PERF_BUFFER_WAIT_BUDGET_HELPER_PATH) |marker| try guard.requireMarker(text_perf_buffer_wait_budget_helper_path, marker);
    const text_phase8_build_path_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_phase8_build_path_path);
    const text_phase8_build_path = try guard.readUtf8File(io, allocator, text_phase8_build_path_path);
    defer allocator.free(text_phase8_build_path);
    for (PHASE8_BUILD_PATH) |marker| try guard.requireMarker(text_phase8_build_path, marker);
    const text_note_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_note_required_markers_path);
    const text_note_required_markers = try guard.readUtf8File(io, allocator, text_note_required_markers_path);
    defer allocator.free(text_note_required_markers);
    for (NOTE_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_note_required_markers, marker);
    const text_bridge_boundary_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_bridge_boundary_required_markers_path);
    const text_bridge_boundary_required_markers = try guard.readUtf8File(io, allocator, text_bridge_boundary_required_markers_path);
    defer allocator.free(text_bridge_boundary_required_markers);
    for (BRIDGE_BOUNDARY_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_bridge_boundary_required_markers, marker);
    const text_scripts_readme_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_scripts_readme_required_markers_path);
    const text_scripts_readme_required_markers = try guard.readUtf8File(io, allocator, text_scripts_readme_required_markers_path);
    defer allocator.free(text_scripts_readme_required_markers);
    for (SCRIPTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_scripts_readme_required_markers, marker);
    const text_tests_readme_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_tests_readme_required_markers_path);
    const text_tests_readme_required_markers = try guard.readUtf8File(io, allocator, text_tests_readme_required_markers_path);
    defer allocator.free(text_tests_readme_required_markers);
    for (TESTS_README_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_tests_readme_required_markers, marker);
    const text_perf_buffer_poll_build_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_poll_build_required_markers_path);
    const text_perf_buffer_poll_build_required_markers = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_build_required_markers_path);
    defer allocator.free(text_perf_buffer_poll_build_required_markers);
    for (PERF_BUFFER_POLL_BUILD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_perf_buffer_poll_build_required_markers, marker);
    const text_phase8_build_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_phase8_build_required_markers_path);
    const text_phase8_build_required_markers = try guard.readUtf8File(io, allocator, text_phase8_build_required_markers_path);
    defer allocator.free(text_phase8_build_required_markers);
    for (PHASE8_BUILD_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_phase8_build_required_markers, marker);
    const text_perf_buffer_poll_test_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_poll_test_required_markers_path);
    const text_perf_buffer_poll_test_required_markers = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_test_required_markers_path);
    defer allocator.free(text_perf_buffer_poll_test_required_markers);
    for (PERF_BUFFER_POLL_TEST_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_perf_buffer_poll_test_required_markers, marker);
    const text_perf_buffer_poll_helper_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_poll_helper_required_markers_path);
    const text_perf_buffer_poll_helper_required_markers = try guard.readUtf8File(io, allocator, text_perf_buffer_poll_helper_required_markers_path);
    defer allocator.free(text_perf_buffer_poll_helper_required_markers);
    for (PERF_BUFFER_POLL_HELPER_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_perf_buffer_poll_helper_required_markers, marker);
    const text_perf_buffer_wait_budget_helper_required_markers_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    defer allocator.free(text_perf_buffer_wait_budget_helper_required_markers_path);
    const text_perf_buffer_wait_budget_helper_required_markers = try guard.readUtf8File(io, allocator, text_perf_buffer_wait_budget_helper_required_markers_path);
    defer allocator.free(text_perf_buffer_wait_budget_helper_required_markers);
    for (PERF_BUFFER_WAIT_BUDGET_HELPER_REQUIRED_MARKERS) |marker| try guard.requireMarker(text_perf_buffer_wait_budget_helper_required_markers, marker);
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}

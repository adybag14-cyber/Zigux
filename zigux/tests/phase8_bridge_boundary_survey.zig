const std = @import("std");

const shared_surveyed_commit = "f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21";

fn expectContains(haystack: []const u8, needle: []const u8) !void {
    try std.testing.expect(std.mem.indexOf(u8, haystack, needle) != null);
}

fn readWorkspaceFile(
    io: anytype,
    allocator: std.mem.Allocator,
    path: []const u8,
    limit: usize,
) ![]u8 {
    return std.Io.Dir.cwd().readFileAlloc(io, path, allocator, .limited(limit));
}

test "phase 8 bridge boundary survey stays wired into the shared packet" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const roadmap = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(roadmap);

    const tests_readme = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/README.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(tests_readme);

    const bridge_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(bridge_note);

    const libbpf_survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(libbpf_survey_note);

    const phase8_build = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase8_build.zig",
        16 * 1024,
    );
    defer std.testing.allocator.free(phase8_build);

    const review_checklist = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/review-checklist.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(review_checklist);

    try expectContains(roadmap, "## Phase 8: Userspace-Adjacent Tooling Expansion");
    try expectContains(roadmap, "tools/lib/subcmd/exec-cmd.c");
    try expectContains(roadmap, "tools/lib/bpf/libbpf.c");
    try expectContains(roadmap, "- `tools/lib/subcmd/*.zig`");
    try expectContains(roadmap, "- `tools/lib/bpf/zigux_segments/`");

    try expectContains(tests_readme, "zigux/tests/phase8_bridge_boundary_survey.zig");
    try expectContains(tests_readme, "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md");
    try expectContains(tests_readme, "zigux/tests/phase8_build.zig");
    try expectContains(tests_readme, "zigux/tests/phase8_perf_buffer_poll.zig");

    try expectContains(bridge_note, "PHASE8_SLICE=userspace-kernel-bridge-boundary-survey");
    try expectContains(bridge_note, "surveyed_commit=" ++ shared_surveyed_commit);
    try expectContains(
        libbpf_survey_note,
        "survey checkpoint: refreshed against inspected `master` head `" ++ shared_surveyed_commit ++ "`",
    );
    try expectContains(bridge_note, "tools/lib/subcmd/exec-cmd.zig");
    try expectContains(bridge_note, "tools/lib/subcmd/help.zig");
    try expectContains(bridge_note, "tools/lib/bpf/zigux_segments/cpu_mask.zig");
    try expectContains(bridge_note, "zigux/tests/phase8_cpu_mask.zig");
    try expectContains(bridge_note, "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig");
    try expectContains(bridge_note, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    try expectContains(bridge_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(bridge_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(bridge_note, "choosePwdCwdFromIdentities()");
    try expectContains(bridge_note, "setupPathWithPwd()");
    try expectContains(bridge_note, "collectExeclArgs()");
    try expectContains(bridge_note, "buildDeferredExecvCall()");
    try expectContains(bridge_note, "planDeferredExecvCall()");
    try expectContains(bridge_note, "buildDeferredExeclCall()");
    try expectContains(bridge_note, "loadCommandListsFromEnvPath()");
    try expectContains(bridge_note, "resolveTerminalDimensions()");
    try expectContains(bridge_note, "writeCommandSectionsForTerminal()");
    try expectContains(bridge_note, "`execv_cmd()`");
    try expectContains(bridge_note, "`execl_cmd()`");
    try expectContains(bridge_note, "`execvp()`");
    try expectContains(bridge_note, "queue ownership");
    try expectContains(bridge_note, "scheduler-facing transport behavior");
    try expectContains(bridge_note, "kernel/workqueue.c");
    try expectContains(bridge_note, "`bpf_token_create()`");
    try expectContains(bridge_note, "perf-buffer-online-cpu-routing");
    try expectContains(bridge_note, "perf_buffer__poll(timeout_ms)");
    try expectContains(bridge_note, "wait-result classification");
    try expectContains(bridge_note, "ready-buffer bookkeeping");
    try expectContains(bridge_note, "no standalone timer helper");
    try expectContains(bridge_note, "no standalone clockevent helper");

    try expectContains(phase8_build, "phase8_bridge_boundary_survey.zig");
    try expectContains(phase8_build, "phase8-bridge-boundary-survey-tests");
    try expectContains(review_checklist, "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md");
    try expectContains(review_checklist, "zigux/tests/phase8_bridge_boundary_survey.zig");
    try expectContains(review_checklist, "file_path_handle_bridge");
    try expectContains(review_checklist, "`execvp()`");
    try expectContains(review_checklist, "`bpf_token_create()`");
    try expectContains(review_checklist, "perf_buffer__poll(timeout_ms)");
}

test "phase 8 bridge boundary survey still matches the live helper surfaces" {
    var io_instance: std.Io.Threaded = .init(std.testing.allocator, .{});
    defer io_instance.deinit();

    const bridge_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(bridge_note);

    const cpu_mask_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-cpu-mask-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(cpu_mask_note);

    const poll_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-perf-buffer-poll-slice.md",
        32 * 1024,
    );
    defer std.testing.allocator.free(poll_note);

    const exec_cmd_helper = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "tools/lib/subcmd/exec-cmd.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(exec_cmd_helper);

    const help_helper = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "tools/lib/subcmd/help.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(help_helper);

    const cpu_mask_helper = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/cpu_mask.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(cpu_mask_helper);

    const cpu_mask_test = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase8_cpu_mask.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(cpu_mask_test);

    const poll_test = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "zigux/tests/phase8_perf_buffer_poll.zig",
        32 * 1024,
    );
    defer std.testing.allocator.free(poll_test);

    const file_path_handle_bridge_helper = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig",
        64 * 1024,
    );
    defer std.testing.allocator.free(file_path_handle_bridge_helper);

    const libbpf_survey_note = try readWorkspaceFile(
        io_instance.io(),
        std.testing.allocator,
        "Documentation/zigux/phase8-libbpf-segment-survey.md",
        64 * 1024,
    );
    defer std.testing.allocator.free(libbpf_survey_note);

    try expectContains(bridge_note, "path-resolution");
    try expectContains(bridge_note, "surveyed_commit=" ++ shared_surveyed_commit);
    try expectContains(
        libbpf_survey_note,
        "survey checkpoint: refreshed against inspected `master` head `" ++ shared_surveyed_commit ++ "`",
    );
    try expectContains(bridge_note, "choosePwdCwdFromIdentities()");
    try expectContains(bridge_note, "setupPathWithPwd()");
    try expectContains(bridge_note, "collectExeclArgs()");
    try expectContains(bridge_note, "raw `PATH` splitting");
    try expectContains(bridge_note, "loadCommandListsFromEnvPath()");
    try expectContains(bridge_note, "resolveTerminalDimensions()");
    try expectContains(bridge_note, "writeCommandSectionsForTerminal()");
    try expectContains(bridge_note, "`execv_cmd()`-style future handoff packaging through `buildDeferredExecvCall()`");
    try expectContains(bridge_note, "the combined launch-free PATH-plus-argv planning wrapper through `planDeferredExecvCall()`");
    try expectContains(bridge_note, "`execl_cmd()`-style argument collection plus deferred future handoff carriers through `buildDeferredExeclCall()`");
    try expectContains(bridge_note, "queue ownership");
    try expectContains(bridge_note, "scheduler-facing transport behavior");
    try expectContains(bridge_note, "kernel/workqueue.c");
    try expectContains(bridge_note, "/proc/<pid>/fdinfo/<fd>");
    try expectContains(bridge_note, "bpf_object_prepare_token()");
    try expectContains(bridge_note, "bpf_object__reuse_map()");
    try expectContains(bridge_note, "Documentation/zigux/phase8-perf-buffer-poll-slice.md");
    try expectContains(bridge_note, "tools/lib/bpf/zigux_segments/perf_buffer_poll.zig");
    try expectContains(bridge_note, "zigux/tests/phase8_perf_buffer_poll.zig");
    try expectContains(bridge_note, "wait-result classification");
    try expectContains(bridge_note, "ready-buffer bookkeeping");
    try expectContains(cpu_mask_note, "a bounded auto-CPU count clamp that mirrors libbpf's perf-buffer map-budget sizing");
    try expectContains(cpu_mask_note, "a pure online-CPU eligibility predicate that mirrors libbpf's automatic-budget offline skip rule");
    try expectContains(cpu_mask_note, "perf-buffer-online-cpu-routing");
    try expectContains(poll_note, "cumulative processed-record count");
    try expectContains(poll_note, "first failing ready buffer");
    try expectContains(poll_note, "no standalone timer helper");
    try expectContains(poll_note, "no standalone clockevent helper");

    try expectContains(exec_cmd_helper, "command_name: []const u8");
    try expectContains(exec_cmd_helper, "exec_path_env: []const u8");
    try expectContains(exec_cmd_helper, "pub fn choosePwdCwdFromIdentities(");
    try expectContains(exec_cmd_helper, "pub fn setupPathWithPwd(");
    try expectContains(exec_cmd_helper, "pub fn collectExeclArgs(");
    try expectContains(exec_cmd_helper, "pub fn buildSearchPath(");
    try expectContains(exec_cmd_helper, "pub fn buildDeferredExecvCall(");
    try expectContains(exec_cmd_helper, "pub fn planDeferredExecvCall(");
    try expectContains(exec_cmd_helper, "pub fn buildDeferredExeclCall(");
    try expectContains(help_helper, "pub fn loadCommandListsFromEnvPath(");
    try expectContains(help_helper, "pub fn resolveTerminalDimensions(");
    try expectContains(help_helper, "pub fn writeCommandSectionsForTerminal(");
    try expectContains(cpu_mask_helper, "pub fn derivePerfBufferAutoCpuCount(possible_cpu_count: usize, map_max_entries: u32) usize {");
    try expectContains(cpu_mask_helper, "pub fn isPerfBufferCpuOnlineEligible(cpu_index: usize, requested_cpu_count: i32, online_mask: []const bool) bool {");
    try expectContains(cpu_mask_helper, "test \"derivePerfBufferAutoCpuCount keeps perf-buffer auto sizing within the map budget\"");
    try expectContains(cpu_mask_helper, "test \"isPerfBufferCpuOnlineEligible keeps the bounded online CPU predicate explicit\"");
    try expectContains(cpu_mask_helper, "test \"isPerfBufferCpuOnlineEligible bypasses the online mask when the caller pins a positive CPU budget\"");
    try expectContains(cpu_mask_test, "test \"phase 8 cpu mask starter slice keeps perf-buffer auto CPU sizing bounded without claiming routing parity\"");
    try expectContains(cpu_mask_test, "test \"phase 8 cpu mask starter slice keeps the online CPU eligibility predicate helper-first\"");
    try expectContains(poll_test, "test \"phase 8 perf-buffer poll docs keep the bounded wait-result helper explicit\"");
    try expectContains(poll_test, "test \"phase 8 perf-buffer poll helper keeps ready-buffer processing fail-fast below epoll parity\"");
    try expectContains(poll_test, "no standalone timer helper");
    try expectContains(poll_test, "no standalone clockevent helper");
    try expectContains(file_path_handle_bridge_helper, "pub fn buildCurrentProcessFdinfoPath(");
    try expectContains(file_path_handle_bridge_helper, "pub fn chooseReusedMapName(");
    try expectContains(file_path_handle_bridge_helper, "pub fn planTokenPreparation(");
    try expectContains(file_path_handle_bridge_helper, "pub fn classifyTokenPreparationFailure(");
}

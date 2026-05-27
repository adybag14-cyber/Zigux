const std = @import("std");

fn readPhase8HelpSlice(b: *std.Build) []const u8 {
    const io = b.graph.io;
    const cwd = std.Io.Dir.cwd();
    return cwd.readFileAlloc(
        io,
        b.pathFromRoot("../../Documentation/zigux/phase8-help-slice.md"),
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-help-slice.md");
}

fn readPhase8KallsymsSlice(b: *std.Build) []const u8 {
    const io = b.graph.io;
    const cwd = std.Io.Dir.cwd();
    return cwd.readFileAlloc(
        io,
        b.pathFromRoot("../../Documentation/zigux/phase8-kallsyms-slice.md"),
        b.allocator,
        .limited(1024 * 1024),
    ) catch @panic("unable to read Documentation/zigux/phase8-kallsyms-slice.md");
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const exec_cmd_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/exec-cmd.zig"),
        .target = target,
        .optimize = optimize,
    });
    const exec_cmd_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_exec_cmd.zig"),
        .target = target,
        .optimize = optimize,
    });
    const exec_cmd_test_options = b.addOptions();
    exec_cmd_test_options.addOption([]const u8, "repo_root", b.pathFromRoot("../.."));
    exec_cmd_root_module.addImport("exec_cmd", exec_cmd_module);
    exec_cmd_root_module.addOptions("build_options", exec_cmd_test_options);

    const exec_cmd_tests = b.addTest(.{
        .name = "phase8-exec-cmd-shared-tests",
        .root_module = exec_cmd_root_module,
    });
    const run_exec_cmd_tests = b.addRunArtifact(exec_cmd_tests);

    const help_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/subcmd/help.zig"),
        .target = target,
        .optimize = optimize,
    });
    const help_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_help.zig"),
        .target = target,
        .optimize = optimize,
    });
    const help_test_options = b.addOptions();
    help_test_options.addOption([]const u8, "phase8_help_slice", readPhase8HelpSlice(b));
    help_root_module.addImport("help", help_module);
    help_root_module.addOptions("phase8_help_options", help_test_options);

    const help_tests = b.addTest(.{
        .name = "phase8-help-shared-tests",
        .root_module = help_root_module,
    });
    const run_help_tests = b.addRunArtifact(help_tests);

    const kallsyms_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/symbol/kallsyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    const kallsyms_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_kallsyms.zig"),
        .target = target,
        .optimize = optimize,
    });
    const kallsyms_test_options = b.addOptions();
    kallsyms_test_options.addOption([]const u8, "phase8_kallsyms_slice", readPhase8KallsymsSlice(b));
    kallsyms_root_module.addImport("kallsyms", kallsyms_module);
    kallsyms_root_module.addOptions("phase8_kallsyms_options", kallsyms_test_options);

    const kallsyms_tests = b.addTest(.{
        .name = "phase8-kallsyms-shared-tests",
        .root_module = kallsyms_root_module,
    });
    const run_kallsyms_tests = b.addRunArtifact(kallsyms_tests);

    const perf_buffer_poll_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_buffer_poll_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_perf_buffer_poll.zig"),
        .target = target,
        .optimize = optimize,
    });
    perf_buffer_poll_root_module.addImport("perf_buffer_poll", perf_buffer_poll_module);

    const perf_buffer_poll_tests = b.addTest(.{
        .name = "phase8-perf-buffer-poll-tests",
        .root_module = perf_buffer_poll_root_module,
    });
    const run_perf_buffer_poll_tests = b.addRunArtifact(perf_buffer_poll_tests);

    const perf_buffer_wait_budget_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_wait_budget.zig"),
        .target = target,
        .optimize = optimize,
    });
    perf_buffer_wait_budget_module.addImport("perf_buffer_poll", perf_buffer_poll_module);
    const perf_buffer_wait_budget_tests = b.addTest(.{
        .name = "phase8-perf-buffer-wait-budget-tests",
        .root_module = perf_buffer_wait_budget_module,
    });
    const run_perf_buffer_wait_budget_tests = b.addRunArtifact(
        perf_buffer_wait_budget_tests,
    );

    const perf_buffer_poll_verify_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_buffer_poll_verify_tests = b.addTest(.{
        .name = "phase8-perf-buffer-poll-verify-tests",
        .root_module = perf_buffer_poll_verify_module,
    });
    const run_perf_buffer_poll_verify_tests = b.addRunArtifact(
        perf_buffer_poll_verify_tests,
    );

    const perf_buffer_ready_window_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_buffer_ready_window_tests = b.addTest(.{
        .name = "phase8-perf-buffer-ready-window-tests",
        .root_module = perf_buffer_ready_window_module,
    });
    const run_perf_buffer_ready_window_tests = b.addRunArtifact(
        perf_buffer_ready_window_tests,
    );

    const ready_buffer_fd_lookup_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ready_buffer_fd_lookup_tests = b.addTest(.{
        .name = "phase8-ready-buffer-fd-lookup-tests",
        .root_module = ready_buffer_fd_lookup_module,
    });
    const run_ready_buffer_fd_lookup_tests = b.addRunArtifact(
        ready_buffer_fd_lookup_tests,
    );

    const file_path_handle_bridge_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    const file_path_handle_bridge_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_file_path_handle_bridge.zig"),
        .target = target,
        .optimize = optimize,
    });
    file_path_handle_bridge_root_module.addImport(
        "file_path_handle_bridge",
        file_path_handle_bridge_module,
    );

    const file_path_handle_bridge_tests = b.addTest(.{
        .name = "phase8-file-path-handle-bridge-tests",
        .root_module = file_path_handle_bridge_root_module,
    });
    const run_file_path_handle_bridge_tests = b.addRunArtifact(
        file_path_handle_bridge_tests,
    );

    const file_path_handle_boundary_guard_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_file_path_handle_boundary_guard.zig"),
        .target = target,
        .optimize = optimize,
    });
    const file_path_handle_boundary_guard_tests = b.addTest(.{
        .name = "phase8-file-path-handle-boundary-guard-tests",
        .root_module = file_path_handle_boundary_guard_root_module,
    });
    const run_file_path_handle_boundary_guard_tests = b.addRunArtifact(
        file_path_handle_boundary_guard_tests,
    );

    const file_path_handle_bridge_manifest_sync_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_file_path_handle_bridge_manifest_sync.zig"),
        .target = target,
        .optimize = optimize,
    });
    const file_path_handle_bridge_manifest_sync_tests = b.addTest(.{
        .name = "phase8-file-path-handle-bridge-manifest-sync-tests",
        .root_module = file_path_handle_bridge_manifest_sync_root_module,
    });
    const run_file_path_handle_bridge_manifest_sync_tests = b.addRunArtifact(
        file_path_handle_bridge_manifest_sync_tests,
    );

    const libbpf_segment_verify_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_segment_verify_tests = b.addTest(.{
        .name = "phase8-libbpf-segment-verify-tests",
        .root_module = libbpf_segment_verify_module,
    });
    const run_libbpf_segment_verify_tests = b.addRunArtifact(
        libbpf_segment_verify_tests,
    );

    const libbpf_segments_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_libbpf_segments.zig"),
        .target = target,
        .optimize = optimize,
    });
    const libbpf_segments_tests = b.addTest(.{
        .name = "phase8-libbpf-segment-compatibility-tests",
        .root_module = libbpf_segments_root_module,
    });
    const run_libbpf_segments_tests = b.addRunArtifact(libbpf_segments_tests);

    const verify_routing_gap_root_module = b.createModule(.{
        .root_source_file = b.path("phase8_verify_routing_gap.zig"),
        .target = target,
        .optimize = optimize,
    });
    const verify_routing_gap_tests = b.addTest(.{
        .name = "phase8-verify-routing-gap-tests",
        .root_module = verify_routing_gap_root_module,
    });
    const run_verify_routing_gap_tests = b.addRunArtifact(verify_routing_gap_tests);

    const test_step = b.step("test", "Run the shared Phase 8 tooling tests.");
    test_step.dependOn(&run_exec_cmd_tests.step);
    test_step.dependOn(&run_help_tests.step);
    test_step.dependOn(&run_kallsyms_tests.step);
    test_step.dependOn(&run_perf_buffer_poll_tests.step);
    test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);
    test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);
    test_step.dependOn(&run_perf_buffer_ready_window_tests.step);
    test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);
    test_step.dependOn(&run_file_path_handle_bridge_tests.step);
    test_step.dependOn(&run_file_path_handle_boundary_guard_tests.step);
    test_step.dependOn(&run_file_path_handle_bridge_manifest_sync_tests.step);
    test_step.dependOn(&run_libbpf_segment_verify_tests.step);
    test_step.dependOn(&run_libbpf_segments_tests.step);
    test_step.dependOn(&run_verify_routing_gap_tests.step);
    b.default_step.dependOn(test_step);
}

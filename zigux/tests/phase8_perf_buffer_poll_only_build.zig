const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const ready_buffer_fd_lookup_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/ready_buffer_fd_lookup.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ready_buffer_fd_lookup_tests = b.addTest(.{
        .name = "phase8-ready-buffer-fd-lookup-tests",
        .root_module = ready_buffer_fd_lookup_module,
    });

    const perf_buffer_poll_verify_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_poll_verify.zig"),
        .target = target,
        .optimize = optimize,
    });
    const perf_buffer_poll_verify_tests = b.addTest(.{
        .name = "phase8-perf-buffer-poll-verify-tests",
        .root_module = perf_buffer_poll_verify_module,
    });

    const run_perf_buffer_poll_tests = b.addRunArtifact(perf_buffer_poll_tests);
    const run_perf_buffer_wait_budget_tests = b.addRunArtifact(perf_buffer_wait_budget_tests);
    const run_ready_buffer_fd_lookup_tests = b.addRunArtifact(ready_buffer_fd_lookup_tests);
    const run_perf_buffer_poll_verify_tests = b.addRunArtifact(perf_buffer_poll_verify_tests);

    const test_step = b.step("test", "Run focused Phase 8 perf-buffer poll tests");
    test_step.dependOn(&run_perf_buffer_poll_tests.step);
    test_step.dependOn(&run_perf_buffer_wait_budget_tests.step);
    test_step.dependOn(&run_ready_buffer_fd_lookup_tests.step);
    test_step.dependOn(&run_perf_buffer_poll_verify_tests.step);
    b.default_step.dependOn(test_step);
}

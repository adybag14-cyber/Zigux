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

    const run_perf_buffer_poll_tests = b.addRunArtifact(perf_buffer_poll_tests);
    const test_step = b.step("test", "Run focused Phase 8 perf-buffer poll tests");
    test_step.dependOn(&run_perf_buffer_poll_tests.step);
}

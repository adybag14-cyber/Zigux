const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const ready_window_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bpf/zigux_segments/perf_buffer_ready_window.zig"),
        .target = target,
        .optimize = optimize,
    });

    const ready_window_tests = b.addTest(.{
        .name = "phase8-perf-buffer-ready-window-tests",
        .root_module = ready_window_module,
    });

    const run_ready_window_tests = b.addRunArtifact(ready_window_tests);
    const test_step = b.step("test", "Run focused Phase 8 ready-buffer window tests.");
    test_step.dependOn(&run_ready_window_tests.step);
    b.default_step.dependOn(test_step);
}

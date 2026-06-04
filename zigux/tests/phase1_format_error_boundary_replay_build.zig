const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const str_error_r_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/str_error_r.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_format_error_boundary_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("str_error_r", str_error_r_module);
    root_module.addImport("vsprintf", vsprintf_module);

    const tests = b.addTest(.{
        .name = "phase1-format-error-boundary-replay-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-format-error-boundary-replay",
        "Run the Phase 1 format/error boundary replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 format/error boundary replay");
    test_step.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_vsprintf_terminator_window_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const vsprintf_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("vsprintf", vsprintf_module);

    const tests = b.addTest(.{
        .name = "phase1-vsprintf-terminator-window-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-vsprintf-terminator-window-replay",
        "Run the Lane 07 vsprintf terminator-window replay from zigux/tests",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 07 vsprintf terminator-window replay",
    );
    test_step.dependOn(&run_tests.step);
}

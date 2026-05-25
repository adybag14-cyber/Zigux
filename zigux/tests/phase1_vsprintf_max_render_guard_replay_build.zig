const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const vsprintf_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/vsprintf.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_vsprintf_max_render_guard_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("vsprintf", vsprintf_module);

    const tests = b.addTest(.{
        .name = "phase1-vsprintf-max-render-guard-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-vsprintf-max-render-guard-replay",
        "Run the standalone Lane 07 vsprintf max-render-guard replay.",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the standalone Lane 07 vsprintf max-render-guard replay.");
    test_step.dependOn(&run_tests.step);
}

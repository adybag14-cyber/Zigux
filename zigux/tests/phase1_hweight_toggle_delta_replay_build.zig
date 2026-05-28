const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_hweight_toggle_delta_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-hweight-toggle-delta-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-hweight-toggle-delta-replay",
        "Run the standalone Phase 1 hweight toggle-delta replay",
    );
    replay_step.dependOn(&run_tests.step);

    const smoke_step = b.step("smoke", "Run the standalone Phase 1 hweight toggle-delta replay");
    smoke_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the standalone Phase 1 hweight toggle-delta replay");
    test_step.dependOn(&run_tests.step);
}

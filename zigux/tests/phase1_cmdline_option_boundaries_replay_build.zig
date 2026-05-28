const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_option_boundaries_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cmdline_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/cmdline.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("cmdline", cmdline_module);

    const tests = b.addTest(.{
        .name = "phase1-cmdline-option-boundaries-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step("phase1-cmdline-option-boundaries-replay", "Run the Phase 1 cmdline option-boundaries replay tests");
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 cmdline option-boundaries replay tests");
    test_step.dependOn(&run_tests.step);
}

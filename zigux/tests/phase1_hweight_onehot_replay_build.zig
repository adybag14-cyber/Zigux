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
        .root_source_file = b.path("phase1_hweight_onehot_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-hweight-onehot-replay",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const replay_step = b.step("phase1-hweight-onehot-replay", "Run the Lane 08 hweight one-hot replay");
    replay_step.dependOn(&run_tests.step);
}

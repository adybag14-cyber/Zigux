const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_shared_replay.zig"),
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
        .name = "phase1-cmdline-shared-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const phase1_cmdline_shared_replay = b.step(
        "phase1-cmdline-shared-replay",
        "Run the focused Phase 1 cmdline shared-replay reminder from zigux/tests",
    );
    phase1_cmdline_shared_replay.dependOn(&run_tests.step);
}

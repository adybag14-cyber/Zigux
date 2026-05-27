const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_prefix_boundary_replay.zig"),
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
        .name = "phase1-cmdline-prefix-boundary-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-cmdline-prefix-boundary-replay",
        "Run the Phase 1 cmdline prefix boundary replay",
    );
    step.dependOn(&run_tests.step);
}

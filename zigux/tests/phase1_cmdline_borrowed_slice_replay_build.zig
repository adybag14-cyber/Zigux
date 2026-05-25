const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_cmdline_borrowed_slice_replay.zig"),
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
        .name = "phase1-cmdline-borrowed-slice-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-cmdline-borrowed-slice-replay",
        "Run the standalone Phase 1 cmdline borrowed-slice replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

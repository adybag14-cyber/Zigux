const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_vsprintf_pad_truncation_replay.zig"),
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
        .name = "phase1-vsprintf-pad-truncation-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-vsprintf-pad-truncation-replay",
        "Run the standalone Phase 1 vsprintf pad/truncation replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

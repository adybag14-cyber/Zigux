const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_argv_split_high_byte_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const argv_split_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/argv_split.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("argv_split", argv_split_module);

    const tests = b.addTest(.{
        .name = "phase1-argv-split-high-byte-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-argv-split-high-byte-replay",
        "Run the Lane 08 argv_split high-byte replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

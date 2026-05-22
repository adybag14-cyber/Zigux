const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_hweight_alias_edges_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const hweight_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/hweight.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("hweight", hweight_module);

    const tests = b.addTest(.{
        .name = "phase1-hweight-alias-edges-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-hweight-alias-edges-replay",
        "Run the standalone Lane 07 hweight alias-edge replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

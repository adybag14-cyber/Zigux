const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_ctype_casefold_boundary_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    const ctype_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/ctype.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ctype", ctype_module);

    const tests = b.addTest(.{
        .name = "phase1-ctype-casefold-boundary-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-ctype-casefold-boundary-replay",
        "Run the Phase 1 ctype casefold and boundary replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

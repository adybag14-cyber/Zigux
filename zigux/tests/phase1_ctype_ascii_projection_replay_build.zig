const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_ctype_ascii_projection_replay.zig"),
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
        .name = "phase1-ctype-ascii-projection-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const replay = b.step(
        "phase1-ctype-ascii-projection-replay",
        "Run the focused Phase 1 ctype ASCII projection replay from zigux/tests",
    );
    replay.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_ctype_boundary_replay.zig"),
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
        .name = "phase1-ctype-boundary-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const phase1_ctype_boundary_replay = b.step(
        "phase1-ctype-boundary-replay",
        "Run the focused Phase 1 ctype boundary replay from zigux/tests",
    );
    phase1_ctype_boundary_replay.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 1 ctype boundary replay");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}

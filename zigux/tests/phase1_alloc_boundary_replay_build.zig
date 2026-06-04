const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const slab_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/slab.zig"),
        .target = target,
        .optimize = optimize,
    });
    const zalloc_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/zalloc.zig"),
        .target = target,
        .optimize = optimize,
    });

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_alloc_boundary_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("slab", slab_module);
    root_module.addImport("zalloc", zalloc_module);

    const tests = b.addTest(.{
        .name = "phase1-alloc-boundary-replay-tests",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-alloc-boundary-replay",
        "Run the Phase 1 allocation boundary replay",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 allocation boundary replay");
    test_step.dependOn(&run_tests.step);
}

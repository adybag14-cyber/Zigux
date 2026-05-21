const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_alias_duplicate_search_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("rbtree", rbtree_module);

    const tests = b.addTest(.{
        .name = "phase1-rbtree-alias-duplicate-search-replay",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase1-rbtree-alias-duplicate-search-replay",
        "Run the Phase 1 rbtree alias duplicate-search replay.",
    );
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(test_step);
}

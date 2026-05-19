const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_edges.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("rbtree", rbtree_module);

    const tests = b.addTest(.{
        .name = "phase1-rbtree-edges",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const step = b.step("phase1-rbtree-edges", "Run the standalone Phase 1 rbtree edge replay");
    step.dependOn(&run_tests.step);
}

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
        .root_source_file = b.path("lane06_rbtree_cached_leftmost_replace.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("rbtree", rbtree_module);

    const tests = b.addTest(.{
        .name = "lane06-rbtree-cached-leftmost-replace",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step("lane06-rbtree-cached-leftmost-replace", "Run Lane 06 rbtree cached leftmost replacement contract");
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run Lane 06 rbtree cached leftmost replacement contract");
    test_step.dependOn(&run_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_root_module.addImport("rbtree_bindings", rbtree_bindings_module);

    const tests = b.addTest(.{
        .name = "phase3-rbtree-test",
        .root_module = test_root_module,
    });
    const run_tests = b.addRunArtifact(tests);
    const test_step = b.step("phase3-rbtree-test", "Run Phase 3 rbtree boundary tests");
    test_step.dependOn(&run_tests.step);

    const dump_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_rbtree_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    dump_root_module.addImport("rbtree_bindings", rbtree_bindings_module);

    const dump = b.addExecutable(.{
        .name = "phase3-rbtree-dump",
        .root_module = dump_root_module,
    });
    const run_dump = b.addRunArtifact(dump);
    const dump_step = b.step("phase3-rbtree-dump", "Run Phase 3 rbtree boundary dump");
    dump_step.dependOn(&run_dump.step);
}

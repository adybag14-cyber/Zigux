const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "phase1-rbtree-replace-traversal-replay",
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_rbtree_replace_traversal_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "rbtree", .module = rbtree_module },
            },
        }),
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase1-rbtree-replace-traversal-replay",
        "Run the focused Phase 1 rbtree replace/traversal replay.",
    );
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(test_step);
}

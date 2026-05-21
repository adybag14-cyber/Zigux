const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_cached_replace_alias_replay.zig"),
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
        .name = "phase1-rbtree-cached-replace-alias-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-rbtree-cached-replace-alias-replay",
        "Run the Lane 07 rbtree cached replacement alias replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_rbtree_alias_state_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("rbtree", b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    }));

    const tests = b.addTest(.{
        .name = "phase1-rbtree-alias-state-replay",
        .root_module = root_module,
    });
    const run = b.addRunArtifact(tests);

    const step = b.step(
        "phase1-rbtree-alias-state-replay",
        "Run the Phase 1 rbtree alias and node-state replay from zigux/tests",
    );
    step.dependOn(&run.step);
}

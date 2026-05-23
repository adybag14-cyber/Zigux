const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const find_bit_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/find_bit.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/bitmap.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_module.addImport("find_bit", find_bit_module);

    const string_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/string.zig"),
        .target = target,
        .optimize = optimize,
    });
    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const replay_module = b.createModule(.{
        .root_source_file = b.path("phase1_helper_ports_a_copyextend_clump_sysfs_cachedleftmost_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    replay_module.addImport("bitmap_helpers", bitmap_module);
    replay_module.addImport("find_bit_helpers", find_bit_module);
    replay_module.addImport("string_helpers", string_module);
    replay_module.addImport("rbtree_helpers", rbtree_module);

    const replay_tests = b.addTest(.{
        .name = "phase1-helper-ports-a-copyextend-clump-sysfs-cachedleftmost-replay",
        .root_module = replay_module,
    });

    const run_replay_tests = b.addRunArtifact(replay_tests);
    const replay_step = b.step(
        "phase1-helper-ports-a-copyextend-clump-sysfs-cachedleftmost-replay",
        "Run the focused Lane 06 helper ports A copy/extend, clump, sysfs, and cached-leftmost replay.",
    );
    replay_step.dependOn(&run_replay_tests.step);

    b.default_step.dependOn(replay_step);
}

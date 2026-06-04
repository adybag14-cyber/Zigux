const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const rbtree_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/rbtree.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_rbtree_cached_bench_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "rbtree", .module = rbtree_module },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const named = b.step(
        "phase1-rbtree-cached-bench-replay",
        "Run the Phase 1 rbtree cached bench replay contract",
    );
    named.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 rbtree cached bench replay tests");
    test_step.dependOn(&run_tests.step);
}

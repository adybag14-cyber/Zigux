const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_list_sort_bench_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "list_sort", .module = list_sort_module },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);

    const replay_step = b.step(
        "phase1-list-sort-bench-replay",
        "Run the Phase 1 list_sort bench replay contract",
    );
    replay_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 list_sort bench replay tests");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

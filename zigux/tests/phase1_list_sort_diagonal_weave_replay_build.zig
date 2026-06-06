const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const list_sort_module = b.createModule(.{
        .root_source_file = b.path("../../tools/lib/list_sort.zig"),
        .target = target,
        .optimize = optimize,
    });

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase1_list_sort_diagonal_weave_replay.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "list_sort", .module = list_sort_module },
        },
    });

    const tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const diagonal_weave_step = b.step(
        "phase1-list-sort-diagonal-weave-replay",
        "Run the Lane 12 list_sort diagonal weave replay",
    );
    diagonal_weave_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 12 list_sort diagonal weave replay");
    test_step.dependOn(&run_tests.step);
}

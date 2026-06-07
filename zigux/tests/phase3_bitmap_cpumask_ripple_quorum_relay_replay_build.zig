const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
        .imports = &.{
            .{ .name = "bitmap_view", .module = bitmap_view },
        },
    });
    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_bitmap_cpumask_ripple_quorum_relay_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "bitmap_view", .module = bitmap_view },
                .{ .name = "cpumask_view", .module = cpumask_view },
            },
        }),
    });
    const run_unit_tests = b.addRunArtifact(tests);

    const named_step = b.step(
        "phase3-bitmap-cpumask-ripple-quorum-relay-replay",
        "Run the Phase 3 bitmap/cpumask ripple quorum relay replay",
    );
    named_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run Phase 3 bitmap/cpumask ripple quorum relay tests");
    test_step.dependOn(&run_unit_tests.step);

    b.default_step.dependOn(&run_unit_tests.step);
}

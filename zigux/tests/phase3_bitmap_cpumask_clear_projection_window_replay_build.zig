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
    });
    cpumask_view.addImport("bitmap_view", bitmap_view);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_bitmap_cpumask_clear_projection_window_replay.zig"),
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "bitmap_view", .module = bitmap_view },
                .{ .name = "cpumask_view", .module = cpumask_view },
            },
        }),
    });

    const run_tests = b.addRunArtifact(tests);
    const step = b.step("phase3-bitmap-cpumask-clear-projection-window-replay", "Run the Phase 3 bitmap/cpumask clear projection replay");
    step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the standalone Phase 3 bitmap/cpumask clear projection replay");
    test_step.dependOn(&run_tests.step);
}

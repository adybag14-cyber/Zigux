const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view = b.addModule("bitmap_view", .{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
    });
    const cpumask_view = b.addModule("cpumask_view", .{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .imports = &.{
            .{ .name = "bitmap_view", .module = bitmap_view },
        },
    });

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_orbital_bridge_replay.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("bitmap_view", bitmap_view);
    test_module.addImport("cpumask_view", cpumask_view);

    const tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step("phase3-bitmap-cpumask-orbital-bridge-replay", "Run Phase 3 bitmap/cpumask orbital bridge replay");
    test_step.dependOn(&run_tests.step);

    const alias = b.step("test", "Run tests");
    alias.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

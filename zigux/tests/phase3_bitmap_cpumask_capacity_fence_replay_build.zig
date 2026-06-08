const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_module = b.addModule("bitmap_view", .{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_module = b.addModule("cpumask_view", .{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_module.addImport("bitmap_view", bitmap_module);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_bitmap_cpumask_capacity_fence_replay.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("bitmap_view", bitmap_module);
    tests.root_module.addImport("cpumask_view", cpumask_module);

    const run_tests = b.addRunArtifact(tests);
    const route = b.step("phase3-bitmap-cpumask-capacity-fence-replay", "Run the Phase 3 bitmap/cpumask capacity fence replay");
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 bitmap/cpumask capacity fence replay");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}

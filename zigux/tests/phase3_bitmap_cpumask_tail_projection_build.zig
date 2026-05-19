const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const uapi_bitmap_cpumask = b.createModule(.{
        .root_source_file = b.path("../uapi/bitmap_cpumask.zig"),
        .target = target,
        .optimize = optimize,
    });
    const bitmap_cpumask_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/bitmap_cpumask.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_cpumask_binding.addImport("uapi_bitmap_cpumask", uapi_bitmap_cpumask);

    const bitmap_view_helper = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_view_helper.addImport("bitmap_cpumask_binding", bitmap_cpumask_binding);

    const cpumask_view_helper = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view_helper.addImport("bitmap_cpumask_binding", bitmap_cpumask_binding);
    cpumask_view_helper.addImport("bitmap_view_helper", bitmap_view_helper);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_tail_projection.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("bitmap_view_helper", bitmap_view_helper);
    root_module.addImport("cpumask_view_helper", cpumask_view_helper);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-bitmap-cpumask-tail-projection-test",
        "Run the Phase 3 bitmap/cpumask tail projection proof",
    );
    test_step.dependOn(&run_unit_tests.step);
}

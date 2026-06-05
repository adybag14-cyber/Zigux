const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    const cpumask_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/cpumask_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    cpumask_view_module.addImport("bitmap_view", bitmap_view_module);

    const err_ptr_module = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value_module.addImport("err_ptr", err_ptr_module);

    const bitmap_cpumask_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_bitmap_cpumask_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    bitmap_cpumask_packet_module.addImport("bitmap_view", bitmap_view_module);
    bitmap_cpumask_packet_module.addImport("cpumask_view", cpumask_view_module);

    const errptr_xarray_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_packet_module.addImport("err_ptr", err_ptr_module);
    errptr_xarray_packet_module.addImport("xa_value", xa_value_module);

    const bitmap_cpumask_tests = b.addTest(.{
        .name = "phase3-bitmap-cpumask-starter-packet",
        .root_module = bitmap_cpumask_packet_module,
    });
    const errptr_xarray_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_packet_module,
    });

    const run_bitmap_cpumask_tests = b.addRunArtifact(bitmap_cpumask_tests);
    const run_errptr_xarray_tests = b.addRunArtifact(errptr_xarray_tests);

    const test_step = b.step(
        "phase3-bitmap-cpumask-errptr-xarray-test",
        "Run the Phase 3 bitmap/cpumask and errptr/xarray starter packets together",
    );
    test_step.dependOn(&run_bitmap_cpumask_tests.step);
    test_step.dependOn(&run_errptr_xarray_tests.step);

    const default_test_step = b.step(
        "test",
        "Run the Phase 3 bitmap/cpumask and errptr/xarray starter packets",
    );
    default_test_step.dependOn(test_step);
}

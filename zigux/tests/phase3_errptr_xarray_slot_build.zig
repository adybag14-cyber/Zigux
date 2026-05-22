const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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

    const xarray_slot_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view_module.addImport("err_ptr", err_ptr_module);
    xarray_slot_view_module.addImport("xa_value", xa_value_module);

    const errptr_xarray_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_root_module.addImport("err_ptr", err_ptr_module);
    errptr_xarray_root_module.addImport("xa_value", xa_value_module);

    const xarray_slot_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_root_module.addImport("err_ptr", err_ptr_module);
    xarray_slot_root_module.addImport("xa_value", xa_value_module);
    xarray_slot_root_module.addImport("xarray_slot_view", xarray_slot_view_module);

    const errptr_xarray_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_root_module,
    });
    const run_errptr_xarray_tests = b.addRunArtifact(errptr_xarray_tests);

    const xarray_slot_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = xarray_slot_root_module,
    });
    const run_xarray_slot_tests = b.addRunArtifact(xarray_slot_tests);

    const test_step = b.step(
        "phase3-errptr-xarray-slot-test",
        "Run the focused Phase 3 err_ptr/xarray and xarray-slot starter packets",
    );
    test_step.dependOn(&run_errptr_xarray_tests.step);
    test_step.dependOn(&run_xarray_slot_tests.step);
}

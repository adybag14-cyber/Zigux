const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });

    const xa_value = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value.addImport("err_ptr", err_ptr);

    const xarray_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view.addImport("err_ptr", err_ptr);
    xarray_slot_view.addImport("xa_value", xa_value);

    const err_ptr_tests = b.addTest(.{
        .name = "phase3-err-ptr-helper-root",
        .root_module = err_ptr,
    });
    const run_err_ptr_tests = b.addRunArtifact(err_ptr_tests);

    const xa_value_tests = b.addTest(.{
        .name = "phase3-xa-value-helper-root",
        .root_module = xa_value,
    });
    const run_xa_value_tests = b.addRunArtifact(xa_value_tests);

    const xarray_slot_view_tests = b.addTest(.{
        .name = "phase3-xarray-slot-view-helper-root",
        .root_module = xarray_slot_view,
    });
    const run_xarray_slot_view_tests = b.addRunArtifact(xarray_slot_view_tests);

    const errptr_xarray_starter_module = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_starter_module.addImport("err_ptr", err_ptr);
    errptr_xarray_starter_module.addImport("xa_value", xa_value);
    const errptr_xarray_starter = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_starter_module,
    });
    const run_errptr_xarray_starter = b.addRunArtifact(errptr_xarray_starter);

    const xarray_slot_starter_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_starter_module.addImport("err_ptr", err_ptr);
    xarray_slot_starter_module.addImport("xa_value", xa_value);
    xarray_slot_starter_module.addImport("xarray_slot_view", xarray_slot_view);
    const xarray_slot_starter = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = xarray_slot_starter_module,
    });
    const run_xarray_slot_starter = b.addRunArtifact(xarray_slot_starter);

    const test_step = b.step(
        "phase3-errptr-xarray-helper-starter-test",
        "Run the Phase 3 helper roots together with the err_ptr/xarray and xarray-slot starter packets",
    );
    test_step.dependOn(&run_err_ptr_tests.step);
    test_step.dependOn(&run_xa_value_tests.step);
    test_step.dependOn(&run_xarray_slot_view_tests.step);
    test_step.dependOn(&run_errptr_xarray_starter.step);
    test_step.dependOn(&run_xarray_slot_starter.step);
}

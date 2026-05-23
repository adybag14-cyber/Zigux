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

    const test_step = b.step(
        "phase3-errptr-xarray-helper-roots-test",
        "Run the Phase 3 err_ptr, xa_value, and xarray_slot_view helper roots together",
    );
    test_step.dependOn(&run_err_ptr_tests.step);
    test_step.dependOn(&run_xa_value_tests.step);
    test_step.dependOn(&run_xarray_slot_view_tests.step);
}

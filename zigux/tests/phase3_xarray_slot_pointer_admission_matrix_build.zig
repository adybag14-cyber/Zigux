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

    const pointer_admission_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_pointer_admission_matrix.zig"),
        .target = target,
        .optimize = optimize,
    });
    pointer_admission_root_module.addImport("err_ptr", err_ptr);
    pointer_admission_root_module.addImport("xa_value", xa_value);
    pointer_admission_root_module.addImport("xarray_slot_view", xarray_slot_view);

    const pointer_admission_tests = b.addTest(.{
        .name = "phase3-xarray-slot-pointer-admission-matrix",
        .root_module = pointer_admission_root_module,
    });

    const run_pointer_admission_tests = b.addRunArtifact(pointer_admission_tests);
    const pointer_admission_step = b.step(
        "phase3-xarray-slot-pointer-admission-matrix",
        "Run the Phase 3 xarray slot pointer admission matrix replay",
    );
    pointer_admission_step.dependOn(&run_pointer_admission_tests.step);
}

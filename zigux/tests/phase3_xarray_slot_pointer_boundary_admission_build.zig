const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const err_ptr_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    xa_value_mod.addImport("err_ptr", err_ptr_mod);

    const xarray_slot_mod = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_mod.addImport("err_ptr", err_ptr_mod);
    xarray_slot_mod.addImport("xa_value", xa_value_mod);

    const pointer_boundary_mod = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_pointer_boundary_admission.zig"),
        .target = target,
        .optimize = optimize,
    });
    pointer_boundary_mod.addImport("err_ptr", err_ptr_mod);
    pointer_boundary_mod.addImport("xa_value", xa_value_mod);
    pointer_boundary_mod.addImport("xarray_slot_view", xarray_slot_mod);

    const pointer_boundary_test = b.addTest(.{
        .name = "phase3-xarray-slot-pointer-boundary-admission-test",
        .root_module = pointer_boundary_mod,
    });

    const run_pointer_boundary_test = b.addRunArtifact(pointer_boundary_test);

    const pointer_boundary_step = b.step(
        "phase3-xarray-slot-pointer-boundary-admission",
        "Run Phase 3 xarray slot pointer boundary admission replay",
    );
    pointer_boundary_step.dependOn(&run_pointer_boundary_test.step);

    const test_step = b.step("test", "Run Phase 3 xarray slot pointer boundary admission tests");
    test_step.dependOn(&run_pointer_boundary_test.step);
}

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

    const errptr_starter_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_starter_root.addImport("err_ptr", err_ptr);
    errptr_starter_root.addImport("xa_value", xa_value);

    const errptr_starter_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_starter_root,
    });
    const run_errptr_starter_tests = b.addRunArtifact(errptr_starter_tests);

    const slot_starter_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    slot_starter_root.addImport("err_ptr", err_ptr);
    slot_starter_root.addImport("xa_value", xa_value);
    slot_starter_root.addImport("xarray_slot_view", xarray_slot_view);

    const slot_starter_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = slot_starter_root,
    });
    const run_slot_starter_tests = b.addRunArtifact(slot_starter_tests);

    const errptr_dump_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_dump_root.addImport("err_ptr", err_ptr);
    errptr_dump_root.addImport("xa_value", xa_value);

    const errptr_dump_exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = errptr_dump_root,
    });
    const run_errptr_dump = b.addRunArtifact(errptr_dump_exe);

    const slot_dump_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    slot_dump_root.addImport("err_ptr", err_ptr);
    slot_dump_root.addImport("xa_value", xa_value);
    slot_dump_root.addImport("xarray_slot_view", xarray_slot_view);

    const slot_dump_exe = b.addExecutable(.{
        .name = "phase3-xarray-slot-dump",
        .root_module = slot_dump_root,
    });
    const run_slot_dump = b.addRunArtifact(slot_dump_exe);

    const full_slice_step = b.step(
        "phase3-errptr-xarray-full-slice-test",
        "Run the Phase 3 err_ptr/xarray helper roots, starter packets, and dump executables together",
    );
    full_slice_step.dependOn(&run_err_ptr_tests.step);
    full_slice_step.dependOn(&run_xa_value_tests.step);
    full_slice_step.dependOn(&run_xarray_slot_view_tests.step);
    full_slice_step.dependOn(&run_errptr_starter_tests.step);
    full_slice_step.dependOn(&run_slot_starter_tests.step);
    full_slice_step.dependOn(&run_errptr_dump.step);
    full_slice_step.dependOn(&run_slot_dump.step);
}

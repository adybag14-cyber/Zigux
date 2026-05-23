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

    const starter_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    starter_root.addImport("err_ptr", err_ptr);
    starter_root.addImport("xa_value", xa_value);
    starter_root.addImport("xarray_slot_view", xarray_slot_view);

    const starter_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = starter_root,
    });
    const run_starter_tests = b.addRunArtifact(starter_tests);

    const dump_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    dump_root.addImport("err_ptr", err_ptr);
    dump_root.addImport("xa_value", xa_value);
    dump_root.addImport("xarray_slot_view", xarray_slot_view);

    const dump_exe = b.addExecutable(.{
        .name = "phase3-xarray-slot-dump",
        .root_module = dump_root,
    });
    const run_dump = b.addRunArtifact(dump_exe);

    const full_slice_step = b.step(
        "phase3-errptr-xarray-full-slice-test",
        "Run the Phase 3 err_ptr/xarray helper roots, starter packet, and dump together",
    );
    full_slice_step.dependOn(&run_err_ptr_tests.step);
    full_slice_step.dependOn(&run_xa_value_tests.step);
    full_slice_step.dependOn(&run_xarray_slot_view_tests.step);
    full_slice_step.dependOn(&run_starter_tests.step);
    full_slice_step.dependOn(&run_dump.step);
}

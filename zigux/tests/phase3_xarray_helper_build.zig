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

    const errptr_xarray_starter = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_starter.addImport("err_ptr", err_ptr);
    errptr_xarray_starter.addImport("xa_value", xa_value);

    const errptr_xarray_tests = b.addTest(.{
        .root_module = errptr_xarray_starter,
    });
    const run_errptr_xarray_tests = b.addRunArtifact(errptr_xarray_tests);

    const xarray_slot_starter = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_starter.addImport("err_ptr", err_ptr);
    xarray_slot_starter.addImport("xa_value", xa_value);
    xarray_slot_starter.addImport("xarray_slot_view", xarray_slot_view);

    const xarray_slot_tests = b.addTest(.{
        .root_module = xarray_slot_starter,
    });
    const run_xarray_slot_tests = b.addRunArtifact(xarray_slot_tests);

    const errptr_xarray_dump = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_dump.addImport("err_ptr", err_ptr);
    errptr_xarray_dump.addImport("xa_value", xa_value);

    const dump_exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = errptr_xarray_dump,
    });
    const run_dump = b.addRunArtifact(dump_exe);

    const test_step = b.step(
        "phase3-xarray-helper-test",
        "Run the Phase 3 err_ptr/xarray starter packet, xarray-slot starter packet, and err_ptr/xarray dump replay",
    );
    test_step.dependOn(&run_errptr_xarray_tests.step);
    test_step.dependOn(&run_xarray_slot_tests.step);
    test_step.dependOn(&run_dump.step);
}

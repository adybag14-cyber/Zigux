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

    const errptr_xarray_starter_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_starter_root.addImport("err_ptr", err_ptr);
    errptr_xarray_starter_root.addImport("xa_value", xa_value);
    const errptr_xarray_starter = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_starter_root,
    });
    const run_errptr_xarray_starter = b.addRunArtifact(errptr_xarray_starter);

    const xarray_slot_starter_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_starter_root.addImport("err_ptr", err_ptr);
    xarray_slot_starter_root.addImport("xa_value", xa_value);
    xarray_slot_starter_root.addImport("xarray_slot_view", xarray_slot_view);
    const xarray_slot_starter = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = xarray_slot_starter_root,
    });
    const run_xarray_slot_starter = b.addRunArtifact(xarray_slot_starter);

    const errptr_xarray_dump_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_dump_root.addImport("err_ptr", err_ptr);
    errptr_xarray_dump_root.addImport("xa_value", xa_value);
    const errptr_xarray_dump = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = errptr_xarray_dump_root,
    });
    const run_errptr_xarray_dump = b.addRunArtifact(errptr_xarray_dump);

    const xarray_slot_dump_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_dump_root.addImport("err_ptr", err_ptr);
    xarray_slot_dump_root.addImport("xa_value", xa_value);
    xarray_slot_dump_root.addImport("xarray_slot_view", xarray_slot_view);
    const xarray_slot_dump = b.addExecutable(.{
        .name = "phase3-xarray-slot-dump",
        .root_module = xarray_slot_dump_root,
    });
    const run_xarray_slot_dump = b.addRunArtifact(xarray_slot_dump);

    const full_packet_step = b.step(
        "phase3-errptr-xarray-full-packet-test",
        "Run the Lane 29 err_ptr/xarray starter packets and dump executables together",
    );
    full_packet_step.dependOn(&run_errptr_xarray_starter.step);
    full_packet_step.dependOn(&run_xarray_slot_starter.step);
    full_packet_step.dependOn(&run_errptr_xarray_dump.step);
    full_packet_step.dependOn(&run_xarray_slot_dump.step);
}

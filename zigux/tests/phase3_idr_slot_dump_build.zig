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

    const idr_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/idr_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_view.addImport("xarray_slot_view", xarray_slot_view);
    idr_slot_view.addImport("xa_value", xa_value);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    root_module.addImport("idr_slot_view", idr_slot_view);

    const dump = b.addExecutable(.{
        .name = "phase3_idr_slot_dump",
        .root_module = root_module,
    });
    const run_dump = b.addRunArtifact(dump);

    const dump_step = b.step(
        "phase3-idr-slot-dump",
        "Run the focused Phase 3 idr-slot dump parity packet",
    );
    dump_step.dependOn(&run_dump.step);
}

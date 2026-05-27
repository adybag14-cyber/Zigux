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

    const ida_slot_view = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_slot_view.addImport("xarray_slot_view", xarray_slot_view);
    ida_slot_view.addImport("xa_value", xa_value);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("ida_slot_view", ida_slot_view);

    const unit_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const test_step = b.step(
        "phase3-ida-slot-starter-packet-test",
        "Run the Phase 3 ida slot starter-packet self-check",
    );
    test_step.dependOn(&run_unit_tests.step);
}

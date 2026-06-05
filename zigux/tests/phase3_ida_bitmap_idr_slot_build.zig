const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const ida_bitmap_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/ida_bitmap_view.zig"),
        .target = target,
        .optimize = optimize,
    });

    const err_ptr_module = b.createModule(.{
        .root_source_file = b.path("../helpers/err_ptr.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xa_value_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xa_value.zig"),
        .target = target,
        .optimize = optimize,
    });
    const xarray_slot_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/xarray_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_view_module.addImport("err_ptr", err_ptr_module);
    xarray_slot_view_module.addImport("xa_value", xa_value_module);

    const idr_slot_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/idr_slot_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_view_module.addImport("xarray_slot_view", xarray_slot_view_module);
    idr_slot_view_module.addImport("xa_value", xa_value_module);

    const ida_bitmap_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_ida_bitmap_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    ida_bitmap_packet_module.addImport("ida_bitmap_view", ida_bitmap_view_module);

    const idr_slot_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_packet_module.addImport("err_ptr", err_ptr_module);
    idr_slot_packet_module.addImport("xa_value", xa_value_module);
    idr_slot_packet_module.addImport("xarray_slot_view", xarray_slot_view_module);
    idr_slot_packet_module.addImport("idr_slot_view", idr_slot_view_module);

    const ida_bitmap_tests = b.addTest(.{
        .name = "phase3-ida-bitmap-starter-packet",
        .root_module = ida_bitmap_packet_module,
    });
    const idr_slot_tests = b.addTest(.{
        .name = "phase3-idr-slot-starter-packet",
        .root_module = idr_slot_packet_module,
    });

    const run_ida_bitmap_tests = b.addRunArtifact(ida_bitmap_tests);
    const run_idr_slot_tests = b.addRunArtifact(idr_slot_tests);

    const test_step = b.step(
        "phase3-ida-bitmap-idr-slot-test",
        "Run the Phase 3 IDA-bitmap and IDR-slot starter packets together",
    );
    test_step.dependOn(&run_ida_bitmap_tests.step);
    test_step.dependOn(&run_idr_slot_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 IDA-bitmap and IDR-slot starter packets");
    default_test_step.dependOn(test_step);
}

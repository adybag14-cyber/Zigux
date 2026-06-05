const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const notifier_view_module = b.createModule(.{
        .root_source_file = b.path("../helpers/notifier_view.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_view_module.addImport("notifier_abi", notifier_abi_module);

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
    xa_value_module.addImport("err_ptr", err_ptr_module);

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

    const notifier_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_notifier_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    notifier_packet_module.addImport("notifier_abi", notifier_abi_module);
    notifier_packet_module.addImport("notifier_view", notifier_view_module);

    const idr_slot_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    idr_slot_packet_module.addImport("err_ptr", err_ptr_module);
    idr_slot_packet_module.addImport("xa_value", xa_value_module);
    idr_slot_packet_module.addImport("xarray_slot_view", xarray_slot_view_module);
    idr_slot_packet_module.addImport("idr_slot_view", idr_slot_view_module);

    const notifier_tests = b.addTest(.{
        .name = "phase3-notifier-starter-packet",
        .root_module = notifier_packet_module,
    });
    const idr_slot_tests = b.addTest(.{
        .name = "phase3-idr-slot-starter-packet",
        .root_module = idr_slot_packet_module,
    });

    const run_notifier_tests = b.addRunArtifact(notifier_tests);
    const run_idr_slot_tests = b.addRunArtifact(idr_slot_tests);

    const test_step = b.step(
        "phase3-notifier-idr-slot-test",
        "Run the Phase 3 notifier and IDR-slot starter packets together",
    );
    test_step.dependOn(&run_notifier_tests.step);
    test_step.dependOn(&run_idr_slot_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 notifier and IDR-slot starter packets");
    default_test_step.dependOn(test_step);
}

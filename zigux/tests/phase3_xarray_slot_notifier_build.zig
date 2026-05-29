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

    const xarray_slot_packet = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_packet.addImport("err_ptr", err_ptr);
    xarray_slot_packet.addImport("xa_value", xa_value);
    xarray_slot_packet.addImport("xarray_slot_view", xarray_slot_view);

    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const xarray_slot_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet-tests",
        .root_module = xarray_slot_packet,
    });
    const run_xarray_slot_tests = b.addRunArtifact(xarray_slot_tests);

    const notifier_abi_tests = b.addTest(.{
        .name = "phase3-notifier-abi-tests",
        .root_module = notifier_abi,
    });
    const run_notifier_abi_tests = b.addRunArtifact(notifier_abi_tests);

    const test_step = b.step(
        "phase3-xarray-slot-notifier-test",
        "Run the Phase 3 xarray-slot starter packet beside the notifier ABI packet",
    );
    test_step.dependOn(&run_xarray_slot_tests.step);
    test_step.dependOn(&run_notifier_abi_tests.step);
}

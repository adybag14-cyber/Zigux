const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });

    const uapi_dev_t_module = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);

    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);

    const version_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("uapi_version", uapi_version_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);

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

    const dev_t_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_packet_module.addImport("uapi_dev_t", uapi_dev_t_module);
    dev_t_packet_module.addImport("dev_t_binding", dev_t_binding_module);
    dev_t_packet_module.addImport("version_binding", version_binding_module);
    dev_t_packet_module.addImport("export_shim", export_shim_module);

    const xarray_slot_packet_module = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_packet_module.addImport("err_ptr", err_ptr_module);
    xarray_slot_packet_module.addImport("xa_value", xa_value_module);
    xarray_slot_packet_module.addImport("xarray_slot_view", xarray_slot_view_module);

    const dev_t_tests = b.addTest(.{
        .name = "phase3-dev-t-starter-packet",
        .root_module = dev_t_packet_module,
    });
    const xarray_slot_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = xarray_slot_packet_module,
    });

    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);
    const run_xarray_slot_tests = b.addRunArtifact(xarray_slot_tests);

    const test_step = b.step(
        "phase3-dev-t-xarray-slot-test",
        "Run the Phase 3 dev_t and xarray-slot starter packets together",
    );
    test_step.dependOn(&run_dev_t_tests.step);
    test_step.dependOn(&run_xarray_slot_tests.step);

    const default_test_step = b.step("test", "Run the Phase 3 dev_t and xarray-slot starter packets");
    default_test_step.dependOn(test_step);
}

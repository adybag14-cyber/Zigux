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

    const xarray_slot_starter_root = b.createModule(.{
        .root_source_file = b.path("phase3_xarray_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    xarray_slot_starter_root.addImport("err_ptr", err_ptr);
    xarray_slot_starter_root.addImport("xa_value", xa_value);
    xarray_slot_starter_root.addImport("xarray_slot_view", xarray_slot_view);

    const errptr_xarray_dump_root = b.createModule(.{
        .root_source_file = b.path("phase3_errptr_xarray_dump.zig"),
        .target = target,
        .optimize = optimize,
    });
    errptr_xarray_dump_root.addImport("err_ptr", err_ptr);
    errptr_xarray_dump_root.addImport("xa_value", xa_value);

    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const uapi_version = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);
    const version_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("uapi_version", uapi_version);
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const dev_t_root = b.createModule(.{
        .root_source_file = b.path("phase3_dev_t_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_root.addImport("uapi_dev_t", uapi_dev_t);
    dev_t_root.addImport("dev_t_binding", dev_t_binding);
    dev_t_root.addImport("version_binding", version_binding);
    dev_t_root.addImport("export_shim", export_shim);

    const starter_tests = b.addTest(.{
        .name = "phase3-errptr-xarray-starter-packet",
        .root_module = errptr_xarray_starter_root,
    });
    const xarray_slot_tests = b.addTest(.{
        .name = "phase3-xarray-slot-starter-packet",
        .root_module = xarray_slot_starter_root,
    });
    const dump_exe = b.addExecutable(.{
        .name = "phase3-errptr-xarray-dump",
        .root_module = errptr_xarray_dump_root,
    });
    const dev_t_tests = b.addTest(.{
        .name = "phase3-dev-t-starter-packet",
        .root_module = dev_t_root,
    });

    const run_starter_tests = b.addRunArtifact(starter_tests);
    const run_xarray_slot_tests = b.addRunArtifact(xarray_slot_tests);
    const run_dump = b.addRunArtifact(dump_exe);
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);

    const test_step = b.step(
        "phase3-xarray-helper-dev-t-test",
        "Run the Phase 3 xarray helper cluster and dev_t starter packet replay",
    );
    test_step.dependOn(&run_starter_tests.step);
    test_step.dependOn(&run_xarray_slot_tests.step);
    test_step.dependOn(&run_dump.step);
    test_step.dependOn(&run_dev_t_tests.step);
}

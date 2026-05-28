const std = @import("std");

fn addPhase3IdrSlotStarterPacket(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
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
        .root_source_file = b.path("phase3_idr_slot_starter_packet.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("err_ptr", err_ptr);
    root_module.addImport("xa_value", xa_value);
    root_module.addImport("xarray_slot_view", xarray_slot_view);
    root_module.addImport("idr_slot_view", idr_slot_view);

    const unit_tests = b.addTest(.{
        .name = "phase3-idr-slot-starter-packet",
        .root_module = root_module,
    });
    return b.addRunArtifact(unit_tests);
}

fn addPhase3ExportUapiLayout(
    b: *std.Build,
    target: std.Build.ResolvedTarget,
    optimize: std.builtin.OptimizeMode,
) *std.Build.Step.Run {
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings.addImport("notifier_abi.zig", notifier_abi);

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
    uapi_version.addImport("abi_bindings", abi_bindings);

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

    const export_shim = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const header_family_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding.addImport("abi_bindings", abi_bindings);
    header_family_binding.addImport("dev_t_binding", dev_t_binding);
    header_family_binding.addImport("version_binding", version_binding);
    header_family_binding.addImport("uapi_version", uapi_version);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_export_uapi_layout.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("uapi_dev_t", uapi_dev_t);
    root_module.addImport("uapi_version", uapi_version);
    root_module.addImport("dev_t_binding", dev_t_binding);
    root_module.addImport("version_binding", version_binding);
    root_module.addImport("header_family_binding", header_family_binding);
    root_module.addImport("export_shim", export_shim);

    const unit_tests = b.addTest(.{
        .name = "phase3-export-uapi-layout",
        .root_module = root_module,
    });
    return b.addRunArtifact(unit_tests);
}

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const phase3_idr_slot_starter_packet = addPhase3IdrSlotStarterPacket(b, target, optimize);
    const phase3_export_uapi_layout = addPhase3ExportUapiLayout(b, target, optimize);

    const phase3_idr_slot_export_step = b.step(
        "phase3-idr-slot-export-test",
        "Run the Phase 3 idr-slot starter packet beside the export/UAPI layout replay",
    );
    phase3_idr_slot_export_step.dependOn(&phase3_idr_slot_starter_packet.step);
    phase3_idr_slot_export_step.dependOn(&phase3_export_uapi_layout.step);
}

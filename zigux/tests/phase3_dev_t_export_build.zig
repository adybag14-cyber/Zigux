const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

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
    const notifier_abi = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings.addImport("notifier_abi", notifier_abi);

    const header_family_binding = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding.addImport("abi_bindings", abi_bindings);
    header_family_binding.addImport("dev_t_binding", dev_t_binding);
    header_family_binding.addImport("version_binding", version_binding);
    header_family_binding.addImport("uapi_version", uapi_version);

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

    const dev_t_tests = b.addTest(.{
        .name = "phase3-dev-t-starter-packet",
        .root_module = dev_t_root,
    });
    const run_dev_t_tests = b.addRunArtifact(dev_t_tests);

    const export_root = b.createModule(.{
        .root_source_file = b.path("phase3_export_uapi_layout.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_root.addImport("uapi_dev_t", uapi_dev_t);
    export_root.addImport("uapi_version", uapi_version);
    export_root.addImport("dev_t_binding", dev_t_binding);
    export_root.addImport("version_binding", version_binding);
    export_root.addImport("header_family_binding", header_family_binding);
    export_root.addImport("export_shim", export_shim);

    const export_tests = b.addTest(.{
        .name = "phase3-export-uapi-layout",
        .root_module = export_root,
    });
    const run_export_tests = b.addRunArtifact(export_tests);

    const test_step = b.step(
        "phase3-dev-t-export-test",
        "Run the Phase 3 dev_t starter packet beside the export/UAPI layout replay",
    );
    test_step.dependOn(&run_dev_t_tests.step);
    test_step.dependOn(&run_export_tests.step);
}

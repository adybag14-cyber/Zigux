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

    const header_family_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/header_family.zig"),
        .target = target,
        .optimize = optimize,
    });
    header_family_binding_module.addImport("abi_bindings", abi_bindings_module);
    header_family_binding_module.addImport("dev_t_binding", dev_t_binding_module);
    header_family_binding_module.addImport("version_binding", version_binding_module);
    header_family_binding_module.addImport("uapi_version", uapi_version_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);

    const export_root_module = b.createModule(.{
        .root_source_file = b.path("phase3_export_uapi_layout.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_root_module.addImport("uapi_dev_t", uapi_dev_t_module);
    export_root_module.addImport("uapi_version", uapi_version_module);
    export_root_module.addImport("dev_t_binding", dev_t_binding_module);
    export_root_module.addImport("version_binding", version_binding_module);
    export_root_module.addImport("header_family_binding", header_family_binding_module);
    export_root_module.addImport("export_shim", export_shim_module);

    const panic_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/panic_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_module.addImport("abi_bindings", abi_bindings_module);

    const allocator_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/allocator_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy_module.addImport("abi_bindings", abi_bindings_module);

    const export_tests = b.addTest(.{
        .name = "phase3-export-policy-pair-export",
        .root_module = export_root_module,
    });
    const panic_tests = b.addTest(.{
        .name = "phase3-export-policy-pair-panic",
        .root_module = panic_policy_module,
    });
    const allocator_tests = b.addTest(.{
        .name = "phase3-export-policy-pair-allocator",
        .root_module = allocator_policy_module,
    });

    const run_export_tests = b.addRunArtifact(export_tests);
    const run_panic_tests = b.addRunArtifact(panic_tests);
    const run_allocator_tests = b.addRunArtifact(allocator_tests);

    const test_step = b.step(
        "phase3-export-policy-pair-test",
        "Run the focused Phase 3 export/UAPI layout plus paired panic and allocator policy replay",
    );
    test_step.dependOn(&run_export_tests.step);
    test_step.dependOn(&run_panic_tests.step);
    test_step.dependOn(&run_allocator_tests.step);
}

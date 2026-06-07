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
    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);

    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    uapi_version_module.addImport("abi_bindings", abi_bindings_module);
    const version_binding_module = b.createModule(.{
        .root_source_file = b.path("../bindings/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("abi_bindings", abi_bindings_module);
    version_binding_module.addImport("uapi_version", uapi_version_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path("../kernel/export_shim.zig"),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_export_status_normalization_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("export_shim", export_shim_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-export-status-normalization-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-export-status-normalization-contract",
        "Run the Lane 26 export status normalization contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 26 export status normalization contract tests.",
    );
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}

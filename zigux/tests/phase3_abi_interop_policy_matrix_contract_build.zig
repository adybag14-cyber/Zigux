const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_path = b.option([]const u8, "abi-bindings-path", "../bindings/abi.zig") orelse "../bindings/abi.zig";
    const notifier_abi_path = b.option([]const u8, "notifier-abi-path", "../bindings/notifier_abi.zig") orelse "../bindings/notifier_abi.zig";
    const export_shim_path = b.option([]const u8, "export-shim-path", "../kernel/export_shim.zig") orelse "../kernel/export_shim.zig";
    const dev_t_binding_path = b.option([]const u8, "dev-t-binding-path", "../bindings/dev_t.zig") orelse "../bindings/dev_t.zig";
    const uapi_dev_t_path = b.option([]const u8, "uapi-dev-t-path", "../uapi/dev_t.zig") orelse "../uapi/dev_t.zig";
    const version_binding_path = b.option([]const u8, "version-binding-path", "../uapi/version.zig") orelse "../uapi/version.zig";

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path(notifier_abi_path),
        .target = target,
        .optimize = optimize,
    });

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings_module.addImport("notifier_abi.zig", notifier_abi_module);

    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path(dev_t_binding_path),
        .target = target,
        .optimize = optimize,
    });

    const uapi_dev_t_module = b.createModule(.{
        .root_source_file = b.path(uapi_dev_t_path),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);

    const version_binding_module = b.createModule(.{
        .root_source_file = b.path(version_binding_path),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("abi_bindings", abi_bindings_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path(export_shim_path),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_interop_policy_matrix_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("export_shim", export_shim_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-interop-policy-matrix-contract",
        .root_module = root_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-interop-policy-matrix-contract",
        "Run the Phase 3 ABI interop-policy matrix contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI interop-policy matrix contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}

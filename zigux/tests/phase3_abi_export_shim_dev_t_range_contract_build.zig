const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const export_shim_path = b.option(
        []const u8,
        "export-shim-path",
        "Path to the export_shim.zig implementation under test.",
    ) orelse "../kernel/export_shim.zig";
    const dev_t_binding_path = b.option(
        []const u8,
        "dev-t-binding-path",
        "Path to the dev_t binding used by the contract.",
    ) orelse "../bindings/dev_t.zig";
    const version_binding_path = b.option(
        []const u8,
        "version-binding-path",
        "Path to the version binding used by export_shim.zig.",
    ) orelse "../bindings/version.zig";

    const notifier_abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/notifier_abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    abi_bindings_module.addImport("notifier_abi", notifier_abi_module);

    const uapi_dev_t_module = b.createModule(.{
        .root_source_file = b.path("../uapi/dev_t.zig"),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding_module = b.createModule(.{
        .root_source_file = b.path(dev_t_binding_path),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding_module.addImport("uapi_dev_t", uapi_dev_t_module);

    const uapi_version_module = b.createModule(.{
        .root_source_file = b.path("../uapi/version.zig"),
        .target = target,
        .optimize = optimize,
    });
    const version_binding_module = b.createModule(.{
        .root_source_file = b.path(version_binding_path),
        .target = target,
        .optimize = optimize,
    });
    version_binding_module.addImport("uapi_version", uapi_version_module);

    const export_shim_module = b.createModule(.{
        .root_source_file = b.path(export_shim_path),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_bindings_module);
    export_shim_module.addImport("dev_t_binding", dev_t_binding_module);
    export_shim_module.addImport("version_binding", version_binding_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_export_shim_dev_t_range_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("export_shim", export_shim_module);
    root_module.addImport("dev_t_binding", dev_t_binding_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-export-shim-dev-t-range-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-export-shim-dev-t-range-contract",
        "Run the Lane 26 export-shim dev_t range contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 26 export-shim dev_t range contract tests.");
    test_step.dependOn(&run_tests.step);
}

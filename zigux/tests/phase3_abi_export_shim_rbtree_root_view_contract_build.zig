const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const export_shim_path = b.option(
        []const u8,
        "export-shim-path",
        "Path to export_shim.zig",
    ) orelse "../kernel/export_shim.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to ABI bindings",
    ) orelse "../bindings/abi.zig";
    const dev_t_binding_path = b.option(
        []const u8,
        "dev-t-binding-path",
        "Path to dev_t binding",
    ) orelse "../bindings/dev_t.zig";
    const version_binding_path = b.option(
        []const u8,
        "version-binding-path",
        "Path to version binding",
    ) orelse "../bindings/version.zig";

    const abi_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_module = b.createModule(.{
        .root_source_file = b.path(dev_t_binding_path),
        .target = target,
        .optimize = optimize,
    });
    const version_module = b.createModule(.{
        .root_source_file = b.path(version_binding_path),
        .target = target,
        .optimize = optimize,
    });
    const export_shim_module = b.createModule(.{
        .root_source_file = b.path(export_shim_path),
        .target = target,
        .optimize = optimize,
    });
    export_shim_module.addImport("abi_bindings", abi_module);
    export_shim_module.addImport("dev_t_binding", dev_t_module);
    export_shim_module.addImport("version_binding", version_module);

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_export_shim_rbtree_root_view_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addImport("export_shim", export_shim_module);

    const contract_tests = b.addTest(.{
        .name = "phase3-abi-export-shim-rbtree-root-view-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "phase3-abi-export-shim-rbtree-root-view-contract",
        "Run the Phase 3 ABI export shim rbtree root-view contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI export shim rbtree root-view contract");
    test_step.dependOn(&run_contract_tests.step);
}

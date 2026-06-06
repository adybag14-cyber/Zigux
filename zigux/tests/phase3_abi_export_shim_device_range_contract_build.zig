const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_path = b.option(
        []const u8,
        "contract-path",
        "Path to the export-shim device-range ABI contract",
    ) orelse "phase3_abi_export_shim_device_range_contract.zig";
    const export_shim_path = b.option(
        []const u8,
        "export-shim-path",
        "Path to zigux/kernel/export_shim.zig",
    ) orelse "../kernel/export_shim.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";
    const dev_t_binding_path = b.option(
        []const u8,
        "dev-t-binding-path",
        "Path to zigux/bindings/dev_t.zig",
    ) orelse "../bindings/dev_t.zig";
    const uapi_dev_t_path = b.option(
        []const u8,
        "uapi-dev-t-path",
        "Path to zigux/uapi/dev_t.zig",
    ) orelse "../uapi/dev_t.zig";
    const version_binding_path = b.option(
        []const u8,
        "version-binding-path",
        "Path to zigux/uapi/version.zig",
    ) orelse "../uapi/version.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const uapi_dev_t = b.createModule(.{
        .root_source_file = b.path(uapi_dev_t_path),
        .target = target,
        .optimize = optimize,
    });
    const dev_t_binding = b.createModule(.{
        .root_source_file = b.path(dev_t_binding_path),
        .target = target,
        .optimize = optimize,
    });
    dev_t_binding.addImport("uapi_dev_t", uapi_dev_t);

    const version_binding = b.createModule(.{
        .root_source_file = b.path(version_binding_path),
        .target = target,
        .optimize = optimize,
    });
    version_binding.addImport("abi_bindings", abi_bindings);

    const export_shim = b.createModule(.{
        .root_source_file = b.path(export_shim_path),
        .target = target,
        .optimize = optimize,
    });
    export_shim.addImport("abi_bindings", abi_bindings);
    export_shim.addImport("dev_t_binding", dev_t_binding);
    export_shim.addImport("version_binding", version_binding);

    const contract = b.createModule(.{
        .root_source_file = b.path(contract_path),
        .target = target,
        .optimize = optimize,
    });
    contract.addImport("export_shim", export_shim);

    const unit_tests = b.addTest(.{ .root_module = contract });
    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "phase3-abi-export-shim-device-range-contract",
        "Run the Phase 3 export-shim device-range ABI contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Phase 3 export-shim device-range ABI contract");
    test_step.dependOn(&run_unit_tests.step);
}

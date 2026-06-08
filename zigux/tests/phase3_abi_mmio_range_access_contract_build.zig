const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const mmio_path = b.option(
        []const u8,
        "mmio-helper-path",
        "path to zigux/helpers/mmio.zig",
    ) orelse "../helpers/mmio.zig";
    const abi_path = b.option(
        []const u8,
        "abi-bindings-path",
        "path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";
    const unsafe_path = b.option(
        []const u8,
        "unsafe-policy-path",
        "path to zigux/unsafe/narrow.zig",
    ) orelse "../unsafe/narrow.zig";

    const abi_module = b.createModule(.{
        .root_source_file = b.path(abi_path),
        .target = target,
        .optimize = optimize,
    });
    const unsafe_module = b.createModule(.{
        .root_source_file = b.path(unsafe_path),
        .target = target,
        .optimize = optimize,
    });
    unsafe_module.addImport("abi_bindings", abi_module);

    const mmio_module = b.createModule(.{
        .root_source_file = b.path(mmio_path),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_module);
    mmio_module.addImport("unsafe_policy", unsafe_module);

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_mmio_range_access_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("abi_bindings", abi_module);
    test_module.addImport("mmio_helper", mmio_module);

    const contract_tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-mmio-range-access-contract",
        "Run the Phase 3 MMIO range access ABI contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}

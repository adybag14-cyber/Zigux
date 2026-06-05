const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_module = b.createModule(.{
        .root_source_file = b.path("../bindings/abi.zig"),
        .target = target,
        .optimize = optimize,
    });
    const narrow_module = b.createModule(.{
        .root_source_file = b.path("../unsafe/narrow.zig"),
        .target = target,
        .optimize = optimize,
    });
    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path("../helpers/unsafe_policy.zig"),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_module);
    unsafe_policy_module.addImport("narrow", narrow_module);

    const mmio_module = b.createModule(.{
        .root_source_file = b.path("../helpers/mmio.zig"),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_module);
    mmio_module.addImport("unsafe_policy", unsafe_policy_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_mmio_range_access_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_module);
    root_module.addImport("mmio_helpers", mmio_module);

    const contract_tests = b.addTest(.{
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-mmio-range-access-contract",
        "Run the Phase 3 ABI MMIO range-access contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI MMIO range-access contract tests");
    test_step.dependOn(&run_contract_tests.step);
}

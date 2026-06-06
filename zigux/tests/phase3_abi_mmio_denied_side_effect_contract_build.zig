const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const mmio_helper_path = b.option(
        []const u8,
        "mmio-helper-path",
        "path to zigux/helpers/mmio.zig",
    ) orelse "../helpers/mmio.zig";
    const abi_binding_path = b.option(
        []const u8,
        "abi-binding-path",
        "path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";
    const unsafe_policy_path = b.option(
        []const u8,
        "unsafe-policy-path",
        "path to zigux/helpers/unsafe_policy.zig",
    ) orelse "../helpers/unsafe_policy.zig";
    const narrow_path = b.option(
        []const u8,
        "narrow-path",
        "path to zigux/unsafe/narrow.zig",
    ) orelse "../unsafe/narrow.zig";

    const contract_mod = b.createModule(.{
        .root_source_file = b.path("phase3_abi_mmio_denied_side_effect_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const abi_mod = b.createModule(.{
        .root_source_file = b.path(abi_binding_path),
        .target = target,
        .optimize = optimize,
    });
    const narrow_mod = b.createModule(.{
        .root_source_file = b.path(narrow_path),
        .target = target,
        .optimize = optimize,
    });
    narrow_mod.addImport("abi_bindings", abi_mod);
    const unsafe_policy_mod = b.createModule(.{
        .root_source_file = b.path(unsafe_policy_path),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_mod.addImport("abi_bindings", abi_mod);
    unsafe_policy_mod.addImport("narrow", narrow_mod);
    const mmio_mod = b.createModule(.{
        .root_source_file = b.path(mmio_helper_path),
        .target = target,
        .optimize = optimize,
    });
    mmio_mod.addImport("abi_bindings", abi_mod);
    mmio_mod.addImport("unsafe_policy", unsafe_policy_mod);
    contract_mod.addImport("abi_bindings", abi_mod);
    contract_mod.addImport("mmio_helpers", mmio_mod);

    const contract_tests = b.addTest(.{
        .root_module = contract_mod,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-mmio-denied-side-effect-contract",
        "Run the Phase 3 ABI MMIO denied side-effect contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run Phase 3 ABI MMIO denied side-effect contract tests");
    test_step.dependOn(&run_contract.step);
}

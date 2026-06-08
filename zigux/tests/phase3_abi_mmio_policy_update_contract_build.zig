const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";
    const mmio_helper_path = b.option(
        []const u8,
        "mmio-helper-path",
        "Path to zigux/helpers/mmio.zig",
    ) orelse "../helpers/mmio.zig";
    const unsafe_policy_path = b.option(
        []const u8,
        "unsafe-policy-path",
        "Path to zigux/helpers/unsafe_policy.zig",
    ) orelse "../helpers/unsafe_policy.zig";
    const narrow_path = b.option(
        []const u8,
        "narrow-path",
        "Path to zigux/unsafe/narrow.zig",
    ) orelse "../unsafe/narrow.zig";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_mmio_policy_update_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const abi_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const narrow_module = b.createModule(.{
        .root_source_file = b.path(narrow_path),
        .target = target,
        .optimize = optimize,
    });
    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path(unsafe_policy_path),
        .target = target,
        .optimize = optimize,
    });
    const mmio_module = b.createModule(.{
        .root_source_file = b.path(mmio_helper_path),
        .target = target,
        .optimize = optimize,
    });

    tests.root_module.addImport("abi_bindings", abi_module);
    tests.root_module.addImport("mmio_helpers", mmio_module);
    mmio_module.addImport("abi_bindings", abi_module);
    mmio_module.addImport("unsafe_policy", unsafe_policy_module);
    unsafe_policy_module.addImport("abi_bindings", abi_module);
    unsafe_policy_module.addImport("narrow", narrow_module);
    narrow_module.addImport("abi_bindings", abi_module);

    const run_contract = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-mmio-policy-update-contract",
        "Run the Phase 3 ABI MMIO direct policy update contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 3 ABI MMIO direct policy update contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}

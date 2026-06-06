const std = @import("std");

pub fn build(b: *std.Build) void {
    const optimize = b.standardOptimizeOption(.{});
    const target = b.standardTargetOptions(.{});

    const test_path = b.option(
        []const u8,
        "contract-path",
        "Path to the Phase 3 MMIO byte-policy width contract",
    ) orelse "phase3_abi_mmio_byte_policy_width_contract.zig";
    const mmio_path = b.option(
        []const u8,
        "mmio-source-path",
        "Path to the Phase 3 MMIO helper source",
    ) orelse "../helpers/mmio.zig";
    const abi_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to the Phase 3 ABI bindings source",
    ) orelse "../bindings/abi.zig";
    const unsafe_policy_path = b.option(
        []const u8,
        "unsafe-policy-path",
        "Path to the Phase 3 unsafe policy source",
    ) orelse "../unsafe/narrow.zig";

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path(test_path),
            .target = target,
            .optimize = optimize,
        }),
    });

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_path),
        .target = target,
        .optimize = optimize,
    });
    const unsafe_policy = b.createModule(.{
        .root_source_file = b.path(unsafe_policy_path),
        .target = target,
        .optimize = optimize,
    });
    const mmio_helpers = b.createModule(.{
        .root_source_file = b.path(mmio_path),
        .target = target,
        .optimize = optimize,
    });

    unsafe_policy.addImport("abi_bindings", abi_bindings);
    mmio_helpers.addImport("abi_bindings", abi_bindings);
    mmio_helpers.addImport("unsafe_policy", unsafe_policy);
    tests.root_module.addImport("abi_bindings", abi_bindings);
    tests.root_module.addImport("mmio_helpers", mmio_helpers);

    const run_tests = b.addRunArtifact(tests);
    const route = b.step(
        "phase3-abi-mmio-byte-policy-width-contract",
        "Run the Phase 3 MMIO byte-policy width contract",
    );
    route.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 MMIO byte-policy width contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}

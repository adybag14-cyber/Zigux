const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const mmio_helper_path = b.option(
        []const u8,
        "mmio-helper-path",
        "path to zigux/helpers/mmio.zig",
    ) orelse "../helpers/mmio.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
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
    narrow_module.addImport("abi_bindings", abi_module);

    const unsafe_policy_module = b.createModule(.{
        .root_source_file = b.path(unsafe_policy_path),
        .target = target,
        .optimize = optimize,
    });
    unsafe_policy_module.addImport("abi_bindings", abi_module);
    unsafe_policy_module.addImport("narrow", narrow_module);

    const mmio_module = b.createModule(.{
        .root_source_file = b.path(mmio_helper_path),
        .target = target,
        .optimize = optimize,
    });
    mmio_module.addImport("abi_bindings", abi_module);
    mmio_module.addImport("unsafe_policy", unsafe_policy_module);

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_mmio_range_view_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("mmio_helper", mmio_module);
    test_module.addImport("abi_bindings", abi_module);

    const tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-mmio-range-view-contract",
        "Run the Phase 3 ABI MMIO range-view contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI MMIO range-view contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}

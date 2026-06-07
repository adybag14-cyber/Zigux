const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_path = b.path("phase3_abi_panic_action_contract.zig");
    const panic_policy_path = b.option(
        []const u8,
        "panic-policy-path",
        "path to zigux/helpers/panic_policy.zig",
    ) orelse "../helpers/panic_policy.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy = b.createModule(.{
        .root_source_file = b.path(panic_policy_path),
        .target = target,
        .optimize = optimize,
    });
    panic_policy.addImport("abi_bindings", abi_bindings);

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = contract_path,
            .target = target,
            .optimize = optimize,
            .imports = &.{
                .{ .name = "panic_policy", .module = panic_policy },
                .{ .name = "abi_bindings", .module = abi_bindings },
            },
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-panic-action-contract",
        "Run the Phase 3 ABI panic action contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 3 ABI panic action contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}

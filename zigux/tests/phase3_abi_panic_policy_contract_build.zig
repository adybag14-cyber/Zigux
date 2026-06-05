const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const abi_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig, relative to this build file",
    ) orelse "../bindings/abi.zig";
    const panic_policy_path = b.option(
        []const u8,
        "panic-policy-path",
        "Path to zigux/helpers/panic_policy.zig, relative to this build file",
    ) orelse "../helpers/panic_policy.zig";

    const abi_mod = b.createModule(.{
        .root_source_file = b.path(abi_path),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy_mod = b.createModule(.{
        .root_source_file = b.path(panic_policy_path),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_mod.addImport("abi_bindings", abi_mod);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_panic_policy_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("abi_bindings", abi_mod);
    tests.root_module.addImport("panic_policy", panic_policy_mod);

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase3-abi-panic-policy-contract",
        "Run the Phase 3 panic-policy ABI substrate contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 panic-policy ABI substrate contract");
    test_step.dependOn(&run_tests.step);
}

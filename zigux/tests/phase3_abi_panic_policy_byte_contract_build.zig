const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to the ABI bindings module",
    ) orelse "../bindings/abi.zig";
    const panic_policy_path = b.option(
        []const u8,
        "panic-policy-path",
        "Path to the panic-policy helper module",
    ) orelse "../helpers/panic_policy.zig";

    const abi_bindings_module = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const panic_policy_helpers_module = b.createModule(.{
        .root_source_file = b.path(panic_policy_path),
        .target = target,
        .optimize = optimize,
    });
    panic_policy_helpers_module.addImport("abi_bindings", abi_bindings_module);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_panic_policy_byte_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings_module);
    root_module.addImport("panic_policy_helpers", panic_policy_helpers_module);

    const tests = b.addTest(.{
        .name = "phase3-abi-panic-policy-byte-contract",
        .root_module = root_module,
    });

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-panic-policy-byte-contract",
        "Run the focused Phase 3 panic-policy byte ABI contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the focused Phase 3 panic-policy byte ABI contract");
    test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}

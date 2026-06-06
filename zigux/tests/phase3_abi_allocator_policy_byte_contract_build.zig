const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const abi_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to the ABI binding module.",
    ) orelse "../bindings/abi.zig";
    const allocator_policy_path = b.option(
        []const u8,
        "allocator-policy-path",
        "Path to the allocator policy helper module.",
    ) orelse "../helpers/allocator_policy.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_path),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path(allocator_policy_path),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_allocator_policy_byte_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("abi_bindings", abi_bindings);
    root_module.addImport("allocator_policy", allocator_policy);

    const tests = b.addTest(.{
        .name = "phase3-abi-allocator-policy-byte-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const test_step = b.step(
        "phase3-abi-allocator-policy-byte-contract",
        "Run the Phase 3 ABI allocator policy byte contract.",
    );
    test_step.dependOn(&run_tests.step);

    const default_test_step = b.step(
        "test",
        "Run the Phase 3 ABI allocator policy byte contract tests.",
    );
    default_test_step.dependOn(&run_tests.step);
    b.default_step.dependOn(&run_tests.step);
}

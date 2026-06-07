const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const allocator_policy_path = b.option(
        []const u8,
        "allocator-policy-path",
        "Path to zigux/helpers/allocator_policy.zig",
    ) orelse "../helpers/allocator_policy.zig";
    const abi_bindings_path = b.option(
        []const u8,
        "abi-bindings-path",
        "Path to zigux/bindings/abi.zig",
    ) orelse "../bindings/abi.zig";

    const abi_bindings = b.createModule(.{
        .root_source_file = b.path(abi_bindings_path),
        .target = target,
        .optimize = optimize,
    });
    const allocator_policy = b.createModule(.{
        .root_source_file = b.path(allocator_policy_path),
        .target = target,
        .optimize = optimize,
    });
    allocator_policy.addImport("abi_bindings", abi_bindings);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase3_abi_allocator_failure_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addImport("allocator_policy", allocator_policy);
    tests.root_module.addImport("abi_bindings", abi_bindings);

    const run_tests = b.addRunArtifact(tests);
    const contract_step = b.step(
        "phase3-abi-allocator-failure-contract",
        "Run the Phase 3 allocator policy failure-boundary ABI contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 3 allocator policy failure-boundary ABI contract");
    test_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);
}

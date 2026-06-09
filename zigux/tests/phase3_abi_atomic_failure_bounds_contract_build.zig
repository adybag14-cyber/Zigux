const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const atomic_helper_path = b.option(
        []const u8,
        "atomic-helper-path",
        "Path to zigux/helpers/atomic.zig",
    ) orelse "../helpers/atomic.zig";

    const atomic_helpers = b.createModule(.{
        .root_source_file = b.path(atomic_helper_path),
        .target = target,
        .optimize = optimize,
    });
    const contract = b.createModule(.{
        .root_source_file = b.path("phase3_abi_atomic_failure_bounds_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract.addImport("atomic_helpers", atomic_helpers);

    const contract_tests = b.addTest(.{
        .root_module = contract,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-atomic-failure-bounds-contract",
        "Run Phase 3 ABI atomic failure bounds contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Phase 3 ABI atomic failure bounds contract");
    test_step.dependOn(&run_contract_tests.step);
    b.default_step.dependOn(&run_contract_tests.step);
}

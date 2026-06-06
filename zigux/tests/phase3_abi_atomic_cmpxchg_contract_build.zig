const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const atomic_helper_path = b.option(
        []const u8,
        "atomic-helper-path",
        "path to zigux/helpers/atomic.zig",
    ) orelse "../helpers/atomic.zig";

    const contract_mod = b.createModule(.{
        .root_source_file = b.path("phase3_abi_atomic_cmpxchg_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const atomic_mod = b.createModule(.{
        .root_source_file = b.path(atomic_helper_path),
        .target = target,
        .optimize = optimize,
    });
    contract_mod.addImport("atomic_helpers", atomic_mod);

    const contract_tests = b.addTest(.{
        .root_module = contract_mod,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-atomic-cmpxchg-contract",
        "Run the Phase 3 ABI atomic compare-exchange wrapper contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run Phase 3 ABI atomic compare-exchange contract tests");
    test_step.dependOn(&run_contract.step);
}

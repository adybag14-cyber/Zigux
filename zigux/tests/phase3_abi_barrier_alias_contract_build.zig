const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const barrier_helper_path = b.option(
        []const u8,
        "barrier-helper-path",
        "path to zigux/helpers/barrier.zig",
    ) orelse "../helpers/barrier.zig";

    const contract_mod = b.createModule(.{
        .root_source_file = b.path("phase3_abi_barrier_alias_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const barrier_mod = b.createModule(.{
        .root_source_file = b.path(barrier_helper_path),
        .target = target,
        .optimize = optimize,
    });
    contract_mod.addImport("barrier_helpers", barrier_mod);

    const contract_tests = b.addTest(.{
        .root_module = contract_mod,
    });
    const run_contract = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-barrier-alias-contract",
        "Run the Phase 3 ABI barrier alias contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run Phase 3 ABI barrier alias contract tests");
    test_step.dependOn(&run_contract.step);
}

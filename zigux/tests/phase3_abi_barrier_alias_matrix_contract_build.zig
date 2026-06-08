const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const barrier_path = b.option(
        []const u8,
        "barrier-helper-path",
        "path to zigux/helpers/barrier.zig",
    ) orelse "../helpers/barrier.zig";

    const test_module = b.createModule(.{
        .root_source_file = b.path("phase3_abi_barrier_alias_matrix_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    test_module.addImport("barrier_helpers", b.createModule(.{
        .root_source_file = b.path(barrier_path),
        .target = target,
        .optimize = optimize,
    }));

    const contract_tests = b.addTest(.{
        .root_module = test_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase3-abi-barrier-alias-matrix-contract",
        "Run the Phase 3 barrier alias matrix ABI contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run tests");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}

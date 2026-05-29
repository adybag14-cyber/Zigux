const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const contract_tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("phase1_find_bit_tail_fixture_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);
    const contract_step = b.step("phase1-find-bit-tail-fixture-contract", "Run the Phase 1 find_bit tail fixture contract");
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the default contract test suite");
    test_step.dependOn(contract_step);
}

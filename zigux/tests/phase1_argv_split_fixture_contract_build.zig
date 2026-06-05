const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_argv_split_fixture_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    const contract_tests = b.addTest(.{
        .name = "phase1-argv-split-fixture-contract",
        .root_module = root_module,
    });

    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "phase1-argv-split-fixture-contract",
        "Run the Lane 09 Phase 1 argv_split fixture contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Lane 09 Phase 1 argv_split fixture contract");
    test_step.dependOn(&run_contract_tests.step);
}

const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const module = b.createModule(.{
        .root_source_file = b.path("lane01_phase10_closure_ledger_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const unit_tests = b.addTest(.{
        .name = "lane01-phase10-closure-ledger-contract",
        .root_module = module,
    });

    const run_unit_tests = b.addRunArtifact(unit_tests);

    const contract_step = b.step(
        "lane01-phase10-closure-ledger-contract",
        "Run the Lane 01 Phase 10 closure ledger package-local contract",
    );
    contract_step.dependOn(&run_unit_tests.step);

    const test_step = b.step("test", "Run the Lane 01 Phase 10 closure ledger package-local contract");
    test_step.dependOn(&run_unit_tests.step);
}

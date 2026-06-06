const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const repo_root = b.option([]const u8, "repo-root", "Repository root to read contract inputs from") orelse ".";

    const contract_module = b.createModule(.{
        .root_source_file = b.path("phase1_closure_validator_checker_roster_contract.zig"),
        .target = target,
        .optimize = optimize,
    });

    const contract_tests = b.addTest(.{
        .name = "phase1-closure-validator-checker-roster-contract",
        .root_module = contract_module,
    });

    const run_contract = b.addRunArtifact(contract_tests);
    run_contract.setCwd(.{ .cwd_relative = repo_root });

    const contract_step = b.step(
        "phase1-closure-validator-checker-roster-contract",
        "Run the Phase 1 closure validator checker roster contract",
    );
    contract_step.dependOn(&run_contract.step);

    const test_step = b.step("test", "Run the Phase 1 closure validator checker roster contract");
    test_step.dependOn(&run_contract.step);

    b.default_step.dependOn(&run_contract.step);
}

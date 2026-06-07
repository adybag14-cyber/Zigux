const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const checker_path = b.option(
        []const u8,
        "checker-path",
        "path to scripts/zigux/check-phase1-bench-live-check-workflow.py",
    ) orelse "scripts/zigux/check-phase1-bench-live-check-workflow.py";

    const checker_options = b.addOptions();
    checker_options.addOption([]const u8, "value", checker_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("check_phase1_bench_live_workflow_checker_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addImport("checker_path", checker_options.createModule());

    const contract_tests = b.addTest(.{
        .name = "check-phase1-bench-live-workflow-checker-contract",
        .root_module = root_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);

    const contract_step = b.step(
        "check-phase1-bench-live-workflow-checker-contract",
        "Run the Phase 1 bench live workflow checker source contract",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run the Phase 1 bench live workflow checker source contract");
    test_step.dependOn(&run_contract_tests.step);

    b.default_step.dependOn(&run_contract_tests.step);
}

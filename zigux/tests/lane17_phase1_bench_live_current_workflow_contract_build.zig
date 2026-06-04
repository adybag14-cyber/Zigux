const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const options = b.addOptions();
    options.addOption(
        []const u8,
        "workflow_path",
        b.option(
            []const u8,
            "workflow-path",
            "Path to .github/workflows/zigux-bootstrap.yml",
        ) orelse ".github/workflows/zigux-bootstrap.yml",
    );

    const contract_module = b.createModule(.{
        .root_source_file = b.path("lane17_phase1_bench_live_current_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    contract_module.addOptions("build_options", options);

    const contract_tests = b.addTest(.{
        .name = "lane17-phase1-bench-live-current-workflow-contract-tests",
        .root_module = contract_module,
    });
    const run_contract_tests = b.addRunArtifact(contract_tests);
    run_contract_tests.setCwd(b.path("../.."));

    const contract_step = b.step(
        "lane17-phase1-bench-live-current-workflow-contract",
        "Validate the live Phase 1 bench workflow cluster",
    );
    contract_step.dependOn(&run_contract_tests.step);

    const test_step = b.step("test", "Run Lane 17 bench live workflow contract tests");
    test_step.dependOn(&run_contract_tests.step);
}

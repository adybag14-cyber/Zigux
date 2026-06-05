const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to the zigux-bootstrap workflow checked by the contract",
    ) orelse ".github/workflows/zigux-bootstrap.yml";
    const route_summary_checker_path = b.option(
        []const u8,
        "route-summary-checker-path",
        "Path to the Phase 1 route-summary checker checked by the contract",
    ) orelse "scripts/zigux/check-phase1-route-summary-counts.py";
    const tests_readme_path = b.option(
        []const u8,
        "tests-readme-path",
        "Path to the tests README checked by the contract",
    ) orelse "zigux/tests/README.md";

    const options = b.addOptions();
    options.addOption([]const u8, "workflow_path", workflow_path);
    options.addOption([]const u8, "route_summary_checker_path", route_summary_checker_path);
    options.addOption([]const u8, "tests_readme_path", tests_readme_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("phase1_route_summary_shared_smoke_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", options);

    const tests = b.addTest(.{
        .name = "phase1-route-summary-shared-smoke-workflow-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "phase1-route-summary-shared-smoke-workflow-contract",
        "Validate the Phase 1 route-summary gate and shared smoke workflow handoff",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Phase 1 route-summary shared-smoke workflow contract");
    test_step.dependOn(&run_tests.step);
}

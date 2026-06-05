const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const tests_readme_path = b.option(
        []const u8,
        "tests-readme-path",
        "Path to zigux/tests/README.md for the Lane 07 shared-reminder workflow contract",
    ) orelse "zigux/tests/README.md";
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml for the Lane 07 shared-reminder workflow contract",
    ) orelse ".github/workflows/zigux-bootstrap.yml";

    const contract_options = b.addOptions();
    contract_options.addOption([]const u8, "tests_readme_path", tests_readme_path);
    contract_options.addOption([]const u8, "workflow_path", workflow_path);

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane07_phase1_shared_reminder_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("contract_options", contract_options);

    const tests = b.addTest(.{
        .name = "lane07-phase1-shared-reminder-workflow-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane07-phase1-shared-reminder-workflow-contract",
        "Run the Lane 07 Phase 1 shared-reminder workflow contract",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the Lane 07 Phase 1 shared-reminder workflow contract");
    test_step.dependOn(&run_tests.step);
}

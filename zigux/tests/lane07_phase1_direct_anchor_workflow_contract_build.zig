const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const options = b.addOptions();
    options.addOption(
        []const u8,
        "tests_readme_path",
        b.option([]const u8, "tests-readme-path", "Path to zigux/tests/README.md") orelse "zigux/tests/README.md",
    );
    options.addOption(
        []const u8,
        "workflow_path",
        b.option([]const u8, "workflow-path", "Path to .github/workflows/zigux-bootstrap.yml") orelse ".github/workflows/zigux-bootstrap.yml",
    );
    options.addOption(
        []const u8,
        "shared_reminder_checker_path",
        b.option([]const u8, "shared-reminder-checker-path", "Path to check-phase1-shared-reminder-packet.py") orelse "scripts/zigux/check-phase1-shared-reminder-packet.py",
    );
    options.addOption(
        []const u8,
        "tests_build_path",
        b.option([]const u8, "tests-build-path", "Path to zigux/tests/build.zig") orelse "zigux/tests/build.zig",
    );

    const root_module = b.createModule(.{
        .root_source_file = b.path("lane07_phase1_direct_anchor_workflow_contract.zig"),
        .target = target,
        .optimize = optimize,
    });
    root_module.addOptions("build_options", options);

    const tests = b.addTest(.{
        .name = "lane07-phase1-direct-anchor-workflow-contract",
        .root_module = root_module,
    });
    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "lane07-phase1-direct-anchor-workflow-contract",
        "Run the Lane 07 Phase 1 direct-anchor workflow contract.",
    );
    contract_step.dependOn(&run_tests.step);

    const test_step = b.step(
        "test",
        "Run the Lane 07 Phase 1 direct-anchor workflow contract tests.",
    );
    test_step.dependOn(&run_tests.step);
}

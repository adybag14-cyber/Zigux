const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    const validator_path = b.option(
        []const u8,
        "validator-path",
        "Path to scripts/zigux/validate-bootstrap.py",
    ) orelse "validate-bootstrap.py";
    const workflow_path = b.option(
        []const u8,
        "workflow-path",
        "Path to .github/workflows/zigux-bootstrap.yml",
    ) orelse "../../.github/workflows/zigux-bootstrap.yml";

    const options = b.addOptions();
    options.addOption([]const u8, "validator_path", validator_path);
    options.addOption([]const u8, "workflow_path", workflow_path);

    const tests = b.addTest(.{
        .root_module = b.createModule(.{
            .root_source_file = b.path("validate_bootstrap_workflow_roster_contract.zig"),
            .target = target,
            .optimize = optimize,
        }),
    });
    tests.root_module.addOptions("build_options", options);

    const run_tests = b.addRunArtifact(tests);

    const contract_step = b.step(
        "validate-bootstrap-workflow-roster-contract",
        "Run the validate-bootstrap workflow roster contract",
    );
    contract_step.dependOn(&run_tests.step);

    b.default_step.dependOn(&run_tests.step);

    const test_step = b.step("test", "Run the validate-bootstrap workflow roster contract");
    test_step.dependOn(&run_tests.step);
}
